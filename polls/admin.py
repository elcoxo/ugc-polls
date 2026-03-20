from django.contrib import admin
from django.utils.html import format_html

from polls.models import (AnswerOption, Poll, PollSession, Question,
                          UserResponse)


class QuestionInline(admin.TabularInline):
    model = Question
    fields = ['text', 'ordering']
    ordering = ['ordering']
    extra = 0
    show_change_link = True


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    fields = ['text', 'order']
    ordering = ['order']
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['id', 'title', 'user', 'questions_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    raw_id_fields = ['user']

    def questions_count(self, obj):
        count = obj.questions.count()
        if count > 0:
            url = f'/admin/polls/question/?poll__id__exact={obj.id}'
            return format_html('<a href="{}">{} вопросов</a>', url, count)
        return '0 вопросов'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('questions')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]
    list_display = ['id', 'poll', 'text', 'ordering', 'options_count', 'created_at']
    list_filter = ['created_at', 'poll']
    search_fields = ['text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['poll']

    def options_count(self, obj):
        count = obj.options.count()
        if count > 0:
            url = f'/admin/polls/answeroption/?question__id__exact={obj.id}'
            return format_html('<a href="{}">{} вариантов</a>', url, count)
        return '0 вариантов'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('poll').prefetch_related('options')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['question']
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'question', 'option', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['session', 'question', 'option']
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'question', 'option')


class UserResponseInline(admin.TabularInline):
    model = UserResponse
    fields = ['question_link', 'option_link', 'created_at']
    readonly_fields = ['question_link', 'option_link', 'created_at']
    extra = 0
    can_delete = False

    def question_link(self, obj):
        url = f'/admin/polls/question/{obj.question_id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.question)

    def option_link(self, obj):
        url = f'/admin/polls/answeroption/{obj.option_id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.option)


@admin.register(PollSession)
class PollSessionAdmin(admin.ModelAdmin):
    inlines = [UserResponseInline]
    list_display = ['id', 'slug', 'user', 'poll', 'created_at', 'finished_at']
    list_filter = ['created_at', 'finished_at']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'poll']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'poll')
