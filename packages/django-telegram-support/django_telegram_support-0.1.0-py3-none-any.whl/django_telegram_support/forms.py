from django import forms
from .conf import MAX_MESSAGE_LEN

class SupportForm(forms.Form):
    email = forms.EmailField(label="Your email", required=True, help_text="We’ll reply here.")
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 8}),
        required=True,
        max_length=MAX_MESSAGE_LEN,
        help_text=f"Up to {MAX_MESSAGE_LEN} characters."
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Invalid submission.")
        return cleaned
