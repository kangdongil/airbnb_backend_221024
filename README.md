## 0.0 개발환경 구축하기
### 0.1 Git 설정하기
- `git` 설치하기
- `cd [PROJECT_FOLDER]`
- `git init`
- `touch .gitignore`
  - [Python_GitIgnore](https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore)
- `git add . && git commit --amend --no-edit`
- `git remote add origin [REPOSITORY_URL}`
- `git push origin main --force`

### 0.2 Python 3.8^ 설치하기
- `Local`
- `GitPod` - Default(3.8.13)
- `GoormIDE`
  ```shell
  sudo apt update && sudo apt install -y python3.8 && sudo update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.8 0
  ``` 

### 0.3 Python Virtual Environment 설정하기: Poetry
1. CLI로 설치하기
  ```shell
  curl -sSL https://install.python-poetry.org | python3 -
  ```
2. `poetry init`
3. `poetry shell`

#### 0.3.1 Poetry 살펴보기
- `poetry init`: 프로젝트를 poetry가 관리하게 하기
- `poetry add [PACKAGE]`: poetry로 python package 설치하기
- `poetry add --dev [PACKAGE]`: 개발자전용 package 설치하기
- `poetry shell`: shell 진입하기
- `exit`: shell 나가기
- `pyproject.toml`: 프로젝트의 명세와 의존성 관리하는 파일

### 0.4 Django Project 시작하기
- `poetry add django`
- `django-admin startproject config .`

#### 0.4.1 Django Project 구조 살펴보기
- `manage.py`
  - Terminal에서 Django 명령을 실행하게 함
- `db.sqlite3`
  - Development 단계에서 Django가 임시로 사용하는 DB 파일
  - 첫 `runserver` 명령과 함께 자동으로 빈 파일로 생성됨
  - `migration`을 통해 코드에 알맞은 DB 모양이 되도록 동기화함.
- `config/`
  - `config.settings`
    - Django Project 관한 모든 설정이 이뤄지는 파일
  - `config.urls`
    - Django Project의 Url들을 관리하는 파일
    - `include`로 App별 url을 묶어 관리하기 좋다

### 0.4.1 Django Project 설정하기
- `config.settings`
  ```python3
  # Allow Gitpod To run Django Server
  ALLOWED_HOSTS = ["localhost"]
  CSRF_TRUSTED_ORIGINS = ["https://*.ws-us72.gitpod.io"]
  # To use Server Timezone
  TIME_ZONE = "Asia/Seoul
  # Modulize INSTALLED_APPS
  SYSTEM_APPS=[ ... ]
  CUSTOM_APPS=[ ... ]
  THIRD_PARTY_APPS=[ ... ]
  INSTALLED_APPS=SYSTEM_APPS+CUSTOM_APPS+THIRD_PARTY_APPS
  ```

### 0.4.2 Django Project Command(`manage.py`) 사용하기
  - `python manage.py [COMMAND]`
  - `runserver`: Django 서버 시작하기
  - `createsuperuser`: Admin 계정 만들기
    - admin 계정을 저장할 DB와 migration이 필요하다
    - DB를 초기화(삭제)할 때마다 admin 계정을 새로 만들어야 한다
  - `makemigrations` >> `migrate`: Model의 변경사항을 DB에 반영하는 행위
    - 세부적으로 `makemigrations`은 파일생성,   
      `migrate`는 변경된 내용을 적용한다.
  - `shell`: Django Shell 켜기
    - `ORM` 등 Django 코드를 콘솔에서 테스트하기 좋다

### 0.5 Django Server 시작하기
1. `python manage.py runserver`
2. `python manage.py makemigrations`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `/admin` 접속하여 admin 계정으로 로그인하기
6. `Admin Panel`을 접속했다면 서버 준비완료

## 1.0 Django Application
- App은 마치 Folder와 같다. 특정 주제의 Data와 그러한 Logic을 한 곳에 모아놓은 곳이다.
### 1.1 App을 Create하고 Configure하기
```shell
python manage.py startapp [APPNAME_PLURAL]
```
- App의 이름은 `복수형`으로 하는게 관행이다
- `apps.py`의 class(`~Config`)을 `config.settings`의 `CUSTOM_APPS`에 추가한다
  ```python3
    CUSTOM_APPS = [
      "users.apps.UsersConfig",
    ]
  ```
### 1.2 App Model를 Create하기
- `django.db.models`를 import하기
- `models.Model`을 inherit한 App Model을 Create하기
  ```python3
  from django.db import models

  class Room(models.Model):
    ...
  ```
#### 1.2.1 Model Field와 종류 살펴보기
- `Field`는 models의 메서드로 특정 속성을 가진 데이터형을 제시한다.
```python3
class Model([]):
  [FIELD] = models.[FieldType](~)
```
- 짧은 텍스트는 `CharField`로 하고, `max_length`를 필수로 가진다
- 긴 텍스트는 `TextField`를 사용한다
- 참거짓값은 `BooleanField`, 양의 정수값은 `PositiveIntegerField`를 사용한다
- 이미지파일은 `ImageField`를 사용하며 파이썬 패키지 `Pillow`를 필요로 한다
- `DateTimeField`는 날짜시간을 표현한다
  - 날짜만 `DateField`, 시간만 `TimeField`
  - `auto_now_add=True`: 처음 생성된 날짜
  - `auto_now=True`: 마지막으로 업데이트한 날짜
#### 1.2.2 `Default` / `Blank` / `Null`
- `Default`는 Client가 값을 입력하지 않았을 때 주는 기본값이며,   
  기존 데이터가 새로운 Field가 추가되었을 때 가지는 값이기도 하다
- `Blank`는 Client 측에서 Form Input을 비웠을 때 허용하는지 여부를 정한다
- `Null`는 DB 측에서 Null값을 허용하는지 여부를 정한다
#### 1.2.3 Model 형태가 달라지면 Migration하기
- Model을 새로 만들거나 수정하였을 때,   
  해당 코드에 맞게 DB형태를 바꾸는 과정을 `migration`이라 한다.
- `python manage.py makemigration`과 `python manage.py migrate`을 연이어 적용한다.
### 1.3 App AdminPanel를 Configure하기
- `django.contrib.admin`를 import하기
- `admin.ModelAdmin`을 inherit한 App Admin을 Create하기
  - Model을 `@(Decorator)`로 언급하기
  ```python3
  from django.contrib import admin
  from . import models

  @admin.register(models.Room)
  class RoomAdmin(admin.ModelAdmin):
    ...
  ```
### 1.3.1 AdminPanel Option 살펴보기
- `list_display`: Admin Panel에 보여줄 Column 속성들을 튜플로 정의하기
```python3
list_display = ("[Field]", ...)
```
- `list_filter`: Admin Panel 우측에 제공할 필터를 튜플로 정의하기
```python3
list_filter = ("[Field]", ...)
```
- `fieldsets`: Admin Panel에서 Data를 생성 또는 수정하는 화면 구성을 정의하기
```python3
fieldsets = (
  ("[Section_Title]", {
    "fields": (~),
    "classes": (~),
  }),
  ...fieldset
)
```
  - `fieldset`: 큰 Section으로 튜플로 정의한다
  - `fields`: Admin Panel에서 다룰 Model Field 정의하기
  - `classes`: FieldSet을 CSS 옵션을 추가한다
    - `wide`: 화면을 더 넓게 사용하기
    - `collapse`: fieldset을 접을 수 있게 한다
  - 항목이 하나인 튜플에 `,`을 넣어 포맷팅으로 사라지는 오류를 방지하자
  ```python3
  {"fields": ("name",),}
  ```
### 1.4 Abstract Model 사용하기
1. `Common` App을 Create하기(Optional)
```bash
django-admin startapp common
```
  - `config.settings`에 `CommonConfig`을 `CUSTOM_APPS`에 추가하기
2. `TimeStampedModel`을 Create하기
  - `created`와 `updated`를 `DateTimeField`로 하기
    - `created`: `auto_now_add`를 `True`하기
    - `updated`: `auto_now`를 `True`하기
3. 내부클래스 `class Meta`에 `abstract=True`하기
```python3
class TimeStampedModel(models.Model):
  class Meta:
    abstract=True
```
  - `abstract=True`하면 해당 Model은 DB에 저장되지 않는다
4. 해당 `Abstract Model`을 `import`하여 사용할 Class에 `inherit`하기
```python3
from common.models import TimeStampedModel

class Model(TimeStampedModel):
  ...
```

## 2.0 User App
- User App을 새로 처음부터 만들기보다 Django에서 제공하는 User App을 확장하는 게 효과적이다
- 첫 migration 전에 미리 Custom User를 세팅하는 것이 바람직하다.
- 만약 이미 어느정도 작업했다면 `db.sqlite3`과 `__init__`파일을 제외한 모든 각 App 폴더의 `migrations/` 파일을 삭제하고 Custom User를 세팅한다.
### 2.1 Custom User App 세팅하기
1. `users` App을 create하기
2. `AUTH_USER_MODEL`을 정하기
   - `config.settings`에 Django User를 inherit 받을 User App을 `AUTH_USER_MODEL`하겠다고 설정한다.
   ```
   AUTH_USER_MODEL = "users.User"
   ```
   - `django.contrib.auth.models.AbstractUser`을 import하기
3. `User Model` 만들기
   - Model의 경우, `models.Model` 대신에 `AbstractUser`을 inherit하기
   ```python3
   from django.contrib.auth.models import AbstractUser
   
   class User(AbstractUser):
     ...
   ```
4. `User AdminPanel` 만들기
   - `django.contrib.auth.admin.UserAdmin`을 import하기
   - Admin의 경우, `admin.UserAdmin` 대신에 `UserAdmin`을 inherit하기
   ```python3
   from django.contrib.auth.admin import UserAdmin
   from . import models
   
   @admin.register(models.User)
   class CustomUserAdmin(UserAdmin):
     ...
   ```

### 2.2 User Model 만들기
- [`AbstractUser`](https://github.com/django/django/blob/main/django/contrib/auth/models.py#L334-L402)가 가진 field를 참고하기
- 기존의 `first_name`과 `last_name`은 사용 안하도록 `editable`을 `False`하기
- 입력이 아닌 선택지를 주려면 `CharField`에 `choices` 항목을 주기
  ```python3
  gender = models.CharField(
    max_length=5,
    choices=GenderChoices.choices,
    default=GenderChoices.MALE,
  )
  ```
- Choices는 내부클래스로 정의한다
  - `django.db.models.TextChoices`를 inherit한다
  - 변수명은 `UPPERCASE`로 정하고, 튜플 안에 첫번째 항목은 DB에 저장되는 값으로 `lowercase`를, 두번째 항목은 Client가 보는 항목으로 `TitleCase`로 표기한다
  ```python3
  class GenderChoices(models.TextChoices):
    MALE = ("male", "Male")
    ...
  ```
### 2.3 User Admin 만들기
- [`UserAdmin`](https://github.com/django/django/blob/main/django/contrib/auth/admin.py#L43-L83) 참고하기
- `fieldsets`을 설정하여 기존 UserAdmin의 항목을 확장한다

### 3.0 Room App & Amenity Model
- `Room`은 여러 `Relationship`을 가진다.   
  User `owner`은 `Room`을 소유하며(`ForeignKey`),   
  `Room`들은 여러 `Amenity`를 가진다(`ManyToManyField`)
- `__str__`을 수정하여 `Room`이 Admin Panel에 어떻게 표현되는지 수정한다
- Admin Panel은 단수형 Model 이름에 단순히 `-s`를 붙여 복수형을 표현한다. 따라서 `Amenities`의 경우 복수형을 직접 표현해주어야 한다
- inherit한 Abstract Model의 Field를 Admin Panel에 드러나게 만들어보자(`read_only`)
### 3.1 Room App을 Create하기
- `ForeignKey`는 `연결할 모델`과 `연결된 모델이 삭제되었을 때 대응`을 언급해야 한다
  - `연결할 모델`은 다음과 같은 방식으로 표시한다
    - `같은 파일 내 모델`의 경우,
    ```python3
    models.ForeignKey("model", on_delete=models.CASCADE)
    ```
    - `다른 App의 모델`의 경우,
    ```python3
    models.ForeignKey("app.model", on_delete=models.CASCADE)
    ```
  - `on_delete`로 연결된 모델이 삭제되었을 때 대응을 정한다
    - `models.CASCADE`: 함께 삭제된다
    - `models.SET_NULL`: 내역이 남는다(`Null=True` 함께 사용)
### 3.2 Amenity App & Admin를 Create하기
- `ManyToManyField`는 1대多 관계를 표현한다.
  ```python3
  models.ManyToManyField("app.model")
  ```
- `AdminPanel`에서 복수형 표현을 수정해야 한다면,
  - `class Meta`로 `verbose_name_plural` 이용하기
  ```python3
  class Amenity(Model):

    class Meta:
      verbose_name_plural = "~"
  ```
- `readonly`한 field를 AdminPanel 수정창에 뜨도록 하려면,
  - `readonly_fields`에 표시한다
  ```python3
  readonly_fields = ("~", ...)
  ```

## 4.0 Experience App & Category App
- `Room` App과 같은 전개로 만들어가되 숙박 개념이 없는 experience는 당일 `시작시간`과 `종료시간`을 가지도록 한다
- `Room`의 부속시설인 `Amenity`처럼 `Experience`는 `Perk`을 `ManytoManyField`로 가진다.
- `Category`는 `Room` 또는 `Experience`의 그룹이다