from django import forms
from .models import RESTAURANT,DISH,MANAGER_REG

class AddRestaurantForm(forms.ModelForm):
    class Meta:
        model = RESTAURANT
        fields = '__all__'
        widgets = {
            'resta_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'time_open': forms.TimeInput(attrs={'class': 'form-control'}),
            'time_close': forms.TimeInput(attrs={'class': 'form-control'}),
            'manager': forms.HiddenInput(),  # 设置为隐藏字段
            'tag': forms.Select(attrs={'class': 'form-control'}),
            'AVG_grade': forms.HiddenInput(),  # 设置为隐藏字段
            'more_Info': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'isopen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].required = False  # 设置为非必填
        self.fields['manager'].initial = None  # 设置初始值为空
        self.fields['AVG_grade'].required = False  # 设置为非必填
        self.fields['AVG_grade'].initial = None  # 设置初始值为空


class AddDish(forms.ModelForm):
    class Meta:
        model =DISH
        fields = '__all__'  # 使用模型中的所有字段
class ApplyRestaurantForm(forms.ModelForm):
    resta_ID = forms.ModelChoiceField(
        queryset=RESTAURANT.objects.filter(manager__isnull=True),
        label="Restaurant"
    )

    class Meta:
        model = MANAGER_REG
        fields = ['resta_ID', 'evidence']  # 只包含需要填写的字段
