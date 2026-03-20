from rest_framework import serializers

from polls.models import Poll, Question, AnswerOption


class PollSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    is_finished = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'slug', 'title', 'user', 'is_finished', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'user', 'created_at', 'updated_at']

    def get_is_finished(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        return getattr(obj, 'is_finished', None)


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'ordering', 'options']


class AnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    option = serializers.PrimaryKeyRelatedField(queryset=AnswerOption.objects.all())

    def validate(self, data):
        session = self.context['session']
        question = data['question']
        option = data['option']

        if question.poll_id != session.poll_id:
            raise serializers.ValidationError('Question does not belong to this poll.')

        if option.question_id != question.id:
            raise serializers.ValidationError('Option does not belong to this question.')

        if session.responses.filter(question=question).exists():
            raise serializers.ValidationError('Question already answered.')

        return data
