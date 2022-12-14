import requests
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework import status
from rest_framework.response import Response
from .models import User
from .serializers import PrivateUserSerializer, PublicUserSerializer
from common.paginations import ListPagination
from rooms.models import Room
from rooms.serializers import HostRoomSerializer
from experiences.models import Experience
from experiences.serializers import HostExperienceSerializer
from reviews.models import Review
from reviews.serializers import UserReviewSerializer, HostReviewSerializer

class MyProfile(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = PrivateUserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            serializer = PrivateUserSerializer(updated_user)
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class PublicProfile(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = PublicUserSerializer(user)
        return Response(serializer.data)


class UserReviews(APIView, ListPagination):
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        
    def get(self, request, username):
        user = self.get_object(username)
        reviews = Review.objects.filter(user=user)\
            .order_by("-created_at")
        serializer = UserReviewSerializer(
            self.paginate(reviews, request),
            many=True,
        )
        return Response({
            "page": self.paginated_info,
            "content": serializer.data,
        })


class HostRooms(APIView, ListPagination):
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound

    def get(self, request, username):
        owner = self.get_object(username)
        if owner.is_host != True:
            raise ParseError("This user is not a host.")
        rooms = Room.objects.filter(owner=owner).order_by("-created_at")
        serializer = HostRoomSerializer(
            self.paginate(rooms, request),
            many=True,
        )
        return Response({
            "page": self.paginated_info(),
            "content": serializer.data,
        })


class HostRoomReviews(APIView, ListPagination):
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
    
    def get(self, request, username):
        owner = self.get_object(username)
        if owner.is_host != True:
            raise ParseError("This user is not a host.")
        reviews = Review.objects.filter(room__owner=owner).order_by("-created_at")
        serializer = HostReviewSerializer(
            self.paginate(reviews, request),
            many=True,
        )
        return Response({
            "page": self.paginated_info,
            "content": serializer.data,
        })


class HostExperiences(APIView, ListPagination):
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound

    def get(self, request, username):
        host = self.get_object(username)
        print(host.is_host)
        if host.is_host != True:
            raise ParseError("This user is not a host.")
        experiences = Experience.objects.filter(host=host).order_by("-created_at")
        serializer = HostExperienceSerializer(
            self.paginate(experiences, request),
            many=True,
        )
        return Response({
            "page": self.paginated_info,
            "content": serializer.data,
        })


class HostExperienceReviews(APIView, ListPagination):
    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
    
    def get(self, request, username):
        host = self.get_object(username)
        if host.is_host != True:
            raise ParseError("This user is not a host.")
        reviews = Review.objects.filter(experience__host=host).order_by("-created_at")
        serializer = HostReviewSerializer(
            self.paginate(reviews, request),
            many=True,
        )
        return Response({
            "page": self.paginated_info,
            "content": serializer.data,
        })


class CreateAccount(APIView):
    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError("Password is required.")
        try:
            validate_password(password)
        except Exception as e:
            raise ParseError(e)
        serializer = PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            new_user.set_password(password)
            new_user.save()
            serializer = PrivateUserSerializer(new_user)
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePassword(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        try:
            validate_password(new_password)
        except Exception as e:
            raise ParseError(e)
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise ParseError("Invalid Password")


class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response({"ok": "Welcome!"})
        else:
            return Response(
                {"error": "Wrong Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogOut(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({"ok": "bye!"})


class GithubLogin(APIView):

    def post(self, request):
        try:
            code = request.data.get("code")
            access_token = requests.post(
                f"https://github.com/login/oauth/access_token?client_id=1bd2d388cbbcf713de7b&code={code}&client_secret={settings.GH_SECRET}",
                headers={
                    "Accept": "application/json",
                },
            )
            access_token = access_token.json().get("access_token")
            user_data = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            ).json()
            user_email = requests.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            ).json()
            user_email = [e for e in user_email if e["primary"] == True][0]
            try:
                user = User.objects.get(email=user_email["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data.get("login"),
                    email=user_email.get("email"),
                    name=user_data.get("name"),
                    avatar=user_data.get("avatar_url"),
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class KakaoLogin(APIView):

    def post(Self, request):
        try:
            code = request.data.get("code")
            print(code)
            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "authorization_code",
                    "client_id": "d10eb532115da07d88f76bde78b9c993",
                    "redirect_uri": "https://3000-kangdongil-gpreactdjang-ijumdskuh65.ws-us77.gitpod.io/social/kakao",
                    "code": code,
                },
            )
            access_token = access_token.json().get("access_token")
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            ).json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            try:
                user = User.objects.get(email=kakao_account.get("email"))
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    email=kakao_account.get("email"),
                    username=profile.get("nickname"),
                    name=profile.get("nickname"),
                    avatar=profile.get("profile_image_url"),
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)