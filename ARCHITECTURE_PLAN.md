# Architektura Backend - Dekoratory, Command Bus, Eventy i Subscribery

## Spis tresci

1. [Dekorator `@authenticate`](#1-dekorator-authenticate)
2. [Dekorator `authorize(permission)`](#2-dekorator-authorizepermission)
3. [Dekorator `@transactional`](#3-dekorator-transactional)
4. [Command Bus](#4-command-bus)
5. [Komendy (Commands)](#5-komendy-commands)
6. [Eventy i Subscribery](#6-eventy-i-subscribery)
7. [Jak to wszystko dziala razem](#7-jak-to-wszystko-dziala-razem)
8. [Jak poprawnie tego uzywac](#8-jak-poprawnie-tego-uzywac)

---

## 1. Dekorator `@authenticate`

**Plik:** `accounts/core/auth/domain/services.py:580`

### Co robi

Sprawdza czy uzytkownik jest uwierzytelniony (zalogowany) zanim wykona sie dekorowana metoda. Jesli nie — rzuca wyjatek i metoda sie nie wykonuje.

### Definicja

```python
def authenticate(func: TFunc) -> TFunc:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        authentication_service = Container().get_object(AuthenticationService)
        authentication_service.authenticate()
        return func(*args, **kwargs)
    return cast(TFunc, wrapper)
```

### Jak dziala

1. Pobiera `AuthenticationService` z kontenera IoC (`haps`).
2. Wywoluje `authentication_service.authenticate()`.
3. Jesli uzytkownik nie jest zalogowany — wyjatek przerwie wykonanie.
4. Jesli jest zalogowany — oryginalna funkcja sie wykonuje normalnie.

### Przyklad uzycia

```python
from accounts.core.auth.domain.services import authenticate

class MyService:
    @authenticate
    def do_something_sensitive(self) -> None:
        # ta metoda wymaga zalogowanego uzytkownika
        ...
```

---

## 2. Dekorator `authorize(permission)`

**Plik:** `accounts/core/auth/domain/services.py:590`

### Co robi

Sprawdza czy zalogowany uzytkownik ma odpowiednie **uprawnienie** (permission) do wykonania danej operacji. Uzywa sie go **po** `@authenticate`.

### Definicja

```python
def authorize(permission: Permission) -> Callable[[TFunc], TFunc]:
    def deco(func: TFunc) -> TFunc:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wrapped_object = args[0]  # self
            Container().get_object(AuthorizationService).authorize(
                permission, wrapped_object
            )
            return func(*args, **kwargs)
        return cast(TFunc, wrapper)
    return cast(Callable[[TFunc], TFunc], deco)
```

### Jak dziala

1. Przyjmuje parametr `permission` (obiekt typu `Permission`).
2. Pobiera `AuthorizationService` z kontenera IoC.
3. Wywoluje `authorization_service.authorize(permission, self)` — przekazuje obiekt (`self`), na ktorym wywolano metode.
4. Jesli uzytkownik nie ma uprawnienia — wyjatek przerwie wykonanie.
5. Jesli ma — metoda sie wykonuje.

### Przyklad uzycia

```python
from accounts.core.auth.domain.services import authorize
from accounts.core.auth.domain.permissions import SomePermission

class MyService:
    @authorize(SomePermission)
    def admin_only_action(self) -> None:
        # wymaga konkretnego uprawnienia
        ...
```

### Roznica miedzy `@authenticate` a `authorize()`

| Cecha | `@authenticate` | `authorize(permission)` |
|-------|-----------------|------------------------|
| Parametry | Brak | Wymaga `Permission` |
| Sprawdza | Czy uzytkownik jest zalogowany | Czy ma konkretne uprawnienie |
| Uzycie | `@authenticate` | `@authorize(SomePermission)` |

---

## 3. Dekorator `@transactional`

**Plik:** `accounts/core/common/repositories/session.py:48`

### Co robi

Zarzadza transakcja bazodanowa (SQLAlchemy Session) oraz dispatchuje eventy po zakonczeniu operacji. To **kluczowy** dekorator — bez niego zmiany w bazie nie zostana zapisane.

### Definicja

```python
def transactional(func: TFunc) -> TFunc:
    @wraps(func)
    @handle_exceptions(RetryOnSpecific(3, 10, OperationalError))
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        event_bus = Container().get_object(EventBus)
        session = Container().get_object(Session)

        try:
            ret = func(*args, **kwargs)
            session.flush()          # sprawdzenie spojnosci bazy
            event_bus.dispatch()     # wykonanie zakolejkowanych eventow
            session.commit()         # zatwierdzenie transakcji
            return ret
        except Exception:
            event_bus.clear()        # wyczyszczenie kolejki eventow
            session.rollback()       # cofniecie transakcji
            raise
        finally:
            session.close()          # zamkniecie sesji

    return cast(TFunc, wrapper)
```

### Jak dziala krok po kroku

1. Pobiera `EventBus` i `Session` z kontenera.
2. Wykonuje dekorowana funkcje.
3. Jesli sukces:
   - `session.flush()` — sprawdza spojnosc z baza (constraints itp.).
   - `event_bus.dispatch()` — wykonuje wszystkie zakolejkowane eventy (subscribery).
   - `session.commit()` — zatwierdza cala transakcje (lacznie ze zmianami z subscriberow).
4. Jesli wyjatek:
   - `event_bus.clear()` — czysci kolejke eventow.
   - `session.rollback()` — cofa wszystkie zmiany.
5. Zawsze zamyka sesje w `finally`.
6. Ma wbudowany retry: 3 proby z 10-sekundowa przerwa na `OperationalError` (zerwane polaczenie z baza).

### Wazne zasady

- **`@transactional` uzywa sie TYLKO na metodzie `handle()` w `BaseCommand`.**
- **NIGDY nie uzywa sie `@transactional` na `SubscriberCommand`** — subscriber juz dziala wewnatrz transakcji (wywolany przez `event_bus.dispatch()` w ramach `@transactional`).

---

## 4. Command Bus

**Interfejs:** `accounts/core/common/interfaces.py:8`
**Implementacja:** `accounts/core/common/command_bus.py:11`

### Co robi

Command Bus to wzorzec, ktory oddziela **wywolanie operacji** od jej **implementacji**. Zamiast bezposrednio tworzyc obiekty komend i wolac na nich metody, przekazujemy klase komendy i parametry do Command Busa.

### Implementacja

```python
@egg
@scope(SINGLETON_SCOPE)
class SimpleCommandBus(CommandBus):
    def execute(
        self, command: Type[BaseCommand], params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        if params:
            command_instance = command(**params)
        else:
            command_instance = command()
        return command_instance.handle()
```

### Jak dziala

1. Przyjmuje **klase** komendy (nie instancje!) i opcjonalne parametry.
2. Tworzy instancje komendy, przekazujac parametry do konstruktora.
3. Wywoluje `command_instance.handle()`.
4. Zwraca wynik.

### Przyklad uzycia (w warstwie API)

```python
class LoginResource:
    command_bus: CommandBus = Inject()

    def on_post(self, req, resp):
        result = cast(
            Result,
            self.command_bus.execute(LoginCommand, params=req.payload)
        )
        resp.payload = result.unwrap()
        resp.status = falcon.HTTP_200
```

---

## 5. Komendy (Commands)

### BaseCommand

**Plik:** `common_utils/core/commands/__init__.py:5`

Bazowa klasa dla wszystkich komend wywolywanych przez Command Bus.

```python
class BaseCommand(ABC):
    def __init__(self, **kwargs: Any) -> None:
        for field in kwargs:
            setattr(self, field, kwargs[field])

    @abstractmethod
    def handle(self) -> Optional[Any]:
        pass
```

### Jak tworzyc komende

```python
from common_utils.core.commands import BaseCommand
from accounts.core.common.repositories.session import transactional
from haps import Inject

class CreateUserCommand(BaseCommand):
    # Zaleznosci wstrzykiwane przez haps
    user_repository: UserRepository = Inject()
    event_bus: EventBus = Inject()

    # Parametry komendy (przekazywane z Command Bus)
    email: Email
    password: Password

    @transactional
    def handle(self) -> Result[UserDTO]:
        user = User.create(email=self.email, password=self.password)
        self.user_repository.save(user)

        # Publikacja eventu — NIE jest od razu wykonany,
        # trafi do kolejki i zostanie zdispatchowany przez @transactional
        self.event_bus.publish(UserCreatedAccountEvent(user_pk=user.pk))

        return Success(UserDTO.from_entity(user))
```

### SubscriberCommand

**Plik:** `common_utils/core/commands/__init__.py:57`

Bazowa klasa dla komend uruchamianych przez subscribery (w reakcji na eventy). **Nie dekoruj ich `@transactional`!**

```python
class SubscriberCommand(ABC):
    def __init__(self, **kwargs: Any) -> None:
        for field in kwargs:
            setattr(self, field, kwargs[field])

    @abstractmethod
    def handle(self) -> Optional[Any]:
        pass
```

### Przyklad SubscriberCommand

```python
class ResetFailedLoginAttemptsLimitCommand(SubscriberCommand):
    user_repository: UserRepository = Inject()
    login_attempts_limit_service: LoginAttemptsLimitService = Inject()

    user_pk: UserPk

    def handle(self) -> None:
        user = self.user_repository.get_by_pk(self.user_pk)
        self.login_attempts_limit_service.reset_limit(email=user.email)
```

---

## 6. Eventy i Subscribery

### Event

**Plik:** `common_utils/infrastructure/events/event.py:7`

Eventy to **niezmienne** (immutable) obiekty reprezentujace zdarzenia domenowe.

```python
class UserCreatedAccountEvent(Event):
    user_pk: UserPk
    occurred_on: datetime
```

Zasady:
- Kazdy event dziedziczy po `Event`.
- Pola sa ustawiane w konstruktorze i **nie mozna ich zmieniac** po inicjalizacji.
- `occurred_on` jest ustawiane automatycznie na `datetime.utcnow()` jesli nie podano.

### Publikacja eventu

Eventy publikuje sie przez `EventBus.publish()` w serwisach domenowych:

```python
self.event_bus.publish(UserSuccessfullyLoggedInEvent(user_pk=user.pk))
```

**Wazne:** `publish()` tylko dodaje event do kolejki. Event jest **wykonywany** dopiero gdy `@transactional` wywola `event_bus.dispatch()`.

### Subscriber

**Plik:** `common_utils/infrastructure/events/dispatchers/sync.py:15`

Subscriber laczy event z komenda, ktora ma sie wykonac w reakcji.

```python
class ResetFailedLoginAttemptsSubscriber(SyncSubscriber):
    command = ResetFailedLoginAttemptsLimitCommand
```

### Rejestracja subscriberow

Subscribery rejestruje sie w `main.py` danego modulu:

```python
def prepare() -> None:
    configure_haps()

    event_bus = Container().get_object(EventBus)

    # Jeden event moze miec wielu subscriberow
    event_bus.subscribe(
        event=UserSuccessfullyLoggedInEvent,
        dispatcher=SyncDispatcher,
        subscribers=[
            ResetFailedLoginAttemptsSubscriber,
        ],
    )

    # Wielu subscriberow na jeden event
    event_bus.subscribe(
        event=UserJoinedCompanyEvent,
        dispatcher=SyncDispatcher,
        subscribers=[
            ActivateB2bSubscriber,
            SetB2bGoalPkSubscriber,
            AbortUserActiveHabitsSubscriber,
        ],
    )
```

### SyncDispatcher

Wykonuje subscribery synchronicznie w ramach tej samej transakcji:

```python
class SyncDispatcher(Dispatcher, ParamsCollector):
    def dispatch(self, event: Event, subscriber: Type[EventSubscriber]) -> None:
        params = self.collect_params(event, sync_subscriber.command)
        cmd = sync_subscriber.command(**params)
        cmd.handle()
```

`ParamsCollector` automatycznie mapuje pola eventu na parametry komendy subscribera (po nazwie).

---

## 7. Jak to wszystko dziala razem

### Pelny przeplyw na przykladzie logowania

```
1. HTTP POST /login
   │
2. LoginResource.on_post()
   │  command_bus.execute(LoginCommand, params={"email": "...", "password": "..."})
   │
3. SimpleCommandBus.execute()
   │  LoginCommand(email="...", password="...").handle()
   │
4. LoginCommand.handle()  ← dekorowany @transactional
   │
   │  ┌─ @transactional otwiera transakcje (Session) ─┐
   │  │                                                 │
   │  │  5. AccountService.login()                      │
   │  │     │                                           │
   │  │     │  6. event_bus.publish(                     │
   │  │     │       UserSuccessfullyLoggedInEvent(...)   │
   │  │     │     )  ← event trafia do kolejki          │
   │  │     │                                           │
   │  │     │  7. return Success(token)                  │
   │  │                                                 │
   │  │  8. session.flush()  ← sprawdzenie bazy         │
   │  │                                                 │
   │  │  9. event_bus.dispatch() ← wykonanie eventow    │
   │  │     │                                           │
   │  │     │  Dla UserSuccessfullyLoggedInEvent:        │
   │  │     │  → ResetFailedLoginAttemptsSubscriber      │
   │  │     │    → ResetFailedLoginAttemptsLimitCommand  │
   │  │     │      .handle()                             │
   │  │                                                 │
   │  │  10. session.commit() ← WSZYSTKO zapisane       │
   │  │                                                 │
   │  └─ session.close() ───────────────────────────────┘
   │
11. Response 200 z tokenem
```

### Kluczowe zaleznosci

```
API Resource
  └─ uzywa → CommandBus.execute(Command, params)
                └─ tworzy → BaseCommand
                              ├─ @transactional na handle()
                              ├─ Inject() do wstrzykiwania serwisow
                              ├─ Serwis domenowy
                              │    └─ EventBus.publish(Event)
                              └─ @transactional:
                                   ├─ session.flush()
                                   ├─ event_bus.dispatch()
                                   │    └─ SyncDispatcher
                                   │         └─ SubscriberCommand.handle()
                                   └─ session.commit()
```

---

## 8. Jak poprawnie tego uzywac

### Tworzenie nowej komendy

1. Utworz klase dziedziczaca po `BaseCommand`.
2. Zdefiniuj parametry jako atrybuty klasy z typami.
3. Wstrzyknij zaleznosci przez `Inject()`.
4. Zaimplementuj `handle()` z dekoratorem `@transactional`.
5. Zwroc wynik opakowany w `Success()` / `Failure()`.

```python
class DoSomethingCommand(BaseCommand):
    my_service: MyService = Inject()
    event_bus: EventBus = Inject()

    param1: str
    param2: int

    @transactional
    def handle(self) -> Result[SomeDTO]:
        result = self.my_service.do_work(self.param1, self.param2)
        self.event_bus.publish(SomethingHappenedEvent(entity_pk=result.pk))
        return Success(SomeDTO.from_entity(result))
```

### Tworzenie nowego subscribera

1. Utworz `SubscriberCommand` (dziedziczacy po `SubscriberCommand`, **NIE** `BaseCommand`).
2. **NIE dodawaj `@transactional`** — subscriber juz dziala w transakcji.
3. Utworz klase subscribera dziedziczaca po `SyncSubscriber`.
4. Zarejestruj subscribera w `main.py`.

```python
# commands/handle_something.py
class HandleSomethingCommand(SubscriberCommand):
    some_repository: SomeRepository = Inject()

    entity_pk: EntityPk  # nazwa musi odpowiadac polu w Event

    def handle(self) -> None:
        entity = self.some_repository.get_by_pk(self.entity_pk)
        entity.do_something()

# events/subscribers.py
class HandleSomethingSubscriber(SyncSubscriber):
    command = HandleSomethingCommand

# main.py
event_bus.subscribe(
    event=SomethingHappenedEvent,
    dispatcher=SyncDispatcher,
    subscribers=[HandleSomethingSubscriber],
)
```

### Zabezpieczanie endpointu

Uzyj `@authenticate` i/lub `authorize()` na metodach serwisow domenowych:

```python
class MyService:
    @authenticate
    def public_but_logged_in_action(self) -> None:
        ...

    @authenticate
    @authorize(AdminPermission)
    def admin_only_action(self) -> None:
        ...
```

### Najczestsze bledy

| Blad | Skutek | Rozwiazanie |
|------|--------|-------------|
| Brak `@transactional` na `BaseCommand.handle()` | Zmiany w bazie nie zostana zapisane, eventy nie zostana zdispatchowane | Dodaj `@transactional` |
| `@transactional` na `SubscriberCommand` | Podwojne commity, bledne zachowanie transakcji | Usun `@transactional` — subscriber dziala juz w transakcji |
| Nazwa pola w `SubscriberCommand` nie zgadza sie z polem w `Event` | `ParamsCollector` nie zmapuje parametrow, subscriber nie dostanie danych | Upewnij sie, ze nazwy pol sa identyczne |
| Brak rejestracji subscribera w `main.py` | Subscriber nigdy sie nie wykona | Dodaj `event_bus.subscribe()` w `prepare()` |
| Bezposrednie tworzenie komendy zamiast uzycia Command Bus | Pominiecie warstwy abstrakcji, trudniejsze testowanie | Zawsze uzywaj `command_bus.execute(Command, params={...})` |
| Wywolanie `event_bus.dispatch()` recznie | Eventy zdispatchowane poza transakcja | Nigdy — `@transactional` robi to automatycznie |
