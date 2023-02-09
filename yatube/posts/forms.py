from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )

    TEXT_LIMIT = 1000
    WORD_LIMIT = 50

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) > self.TEXT_LIMIT:
            raise forms.ValidationError(
                f"Ограничение поста в {self.TEXT_LIMIT} символов"
            )
        for word in data.split():
            if len(word) > self.WORD_LIMIT:
                raise forms.ValidationError(
                    f"Максимальная длина слова - {self.WORD_LIMIT} символов"
                )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            "text",
        )
