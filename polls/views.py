from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (SAFE_METHODS, AllowAny, BasePermission,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.paginations import BasePageNumberPagination
from polls.helpers import get_next_question
from polls.models import Poll, PollSession, UserResponse
from polls.serializers import (AnswerSerializer, PollSerializer,
                               QuestionSerializer)


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class PollViewSet(ModelViewSet):
    serializer_class = PollSerializer
    pagination_class = BasePageNumberPagination
    lookup_field = 'slug'

    def get_queryset(self):
        if self.action in ('list', 'retrieve', 'start'):
            queryset = Poll.objects.all()
        else:
            queryset = Poll.objects.filter(user=self.request.user)

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_finished=Exists(
                    PollSession.objects.filter(
                        poll=OuterRef('pk'),
                        user=self.request.user,
                        finished_at__isnull=False,
                    )
                )
            )

        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(request=None)
    @action(detail=True, methods=['POST'])
    def start(self, request, slug=None):
        """Создает сессию и возвращает первый вопрос"""
        poll = self.get_object()
        session, created = PollSession.objects.get_or_create(user=request.user, poll=poll)
        if session.is_finished:
            return Response({'detail': 'Poll already completed.'}, status=HTTP_400_BAD_REQUEST)

        if not (question := get_next_question(session)):
            return Response({'detail': 'Poll has no questions.'}, status=HTTP_400_BAD_REQUEST)

        return Response({
            'session_slug': session.slug,
            'question': QuestionSerializer(question).data,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class PollSessionViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return PollSession.objects.filter(
            user=self.request.user,
        ).select_related('poll')

    def get_object(self):
        session = get_object_or_404(
            self.get_queryset(),
            slug=self.kwargs['slug'],
            finished_at__isnull=True,
        )
        self.check_object_permissions(self.request, session)
        return session

    @action(detail=True, methods=['GET'])
    def question(self, request, slug=None):
        """Возвращает текущий вопрос"""
        session = self.get_object()

        next_question = get_next_question(session)
        if next_question is None:
            return Response({'completed': True})

        return Response(QuestionSerializer(next_question).data)

    @extend_schema(request=AnswerSerializer)
    @action(detail=True, methods=['POST'])
    def answer(self, request, slug=None):
        """Сохраняет ответ на текущий вопрос"""
        session = self.get_object()

        serializer = AnswerSerializer(data=request.data, context={'session': session})
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']
        option = serializer.validated_data['option']

        with transaction.atomic():
            UserResponse.objects.create(session=session, question=question, option=option)
            next_question = get_next_question(session)
            if next_question is None:
                session.finished_at = timezone.now()
                session.save(update_fields=['finished_at'])
                return Response({'completed': True})

        return Response(QuestionSerializer(next_question).data)
