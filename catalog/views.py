from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import AddRestaurantForm,AddDish,ApplyRestaurantForm
# # 导入模块
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views import generic
# Create your views here.
from .models import RESTAURANT, DISH, COMMENT, REPLY, DELETE_RESTA
from zoneinfo import ZoneInfo
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required




def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_users=0
    # Available books (status = 'a')
    num_restaurants=RESTAURANT.objects.count()  # The 'all()' is implied by default.
    managers = User.objects.all()  # 假设所有用户都是经理
    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'managers': managers,'num_users':num_users,'num_restaurants':num_restaurants},
    )

class RestaurantListView(generic.ListView):
    model = RESTAURANT
    template_name = 'catalog/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        location = self.request.GET.get('location')
        tag = self.request.GET.get('tag')
        # 使用ZoneInfo获取上海时区
        shanghai_timezone = ZoneInfo('Asia/Shanghai')
        current_time = timezone.now().astimezone(shanghai_timezone)
        # Filter by current time within time_open and time_close
        queryset = queryset.filter(
            Q(time_open__lte=current_time, time_close__gte=current_time) |
            Q(time_open__isnull=True) | Q(time_close__isnull=True)
        )
        queryset = queryset.filter(isopen=True)
        if search_query:
            queryset = queryset.filter(
                Q(resta_name__icontains=search_query) |
                Q(dish__dish_name__icontains=search_query) |
                Q(more_Info__icontains=search_query)
            ).distinct()
        queryset = queryset.order_by('-AVG_grade')
        if location:
            queryset = queryset.filter(location=location)
        if tag:
            queryset = queryset.filter(tag=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        context['search_query'] = search_query
        context['location'] = self.request.GET.get('location', '')
        context['location_choices'] = RESTAURANT.location_choice
        context['tag'] = self.request.GET.get('tag', '')
        context['tag_choices'] = RESTAURANT.tag_choice

        if search_query:
            for restaurant in context['restaurants']:
                if search_query.lower() in restaurant.resta_name.lower() or search_query.lower() in restaurant.more_Info.lower():
                    # 搜索内容是餐厅名称时，显示最多5个菜品
                    restaurant.filtered_dishes = restaurant.dish_set.filter(onsale=True)[:5]
                else:
                    # 否则，显示匹配搜索内容的菜品
                    restaurant.filtered_dishes = restaurant.dish_set.filter(dish_name__icontains=search_query, onsale=True)[:5]
        else:
            # 没有搜索内容时，显示在售的菜品（最多五个）
            for restaurant in context['restaurants']:
                restaurant.filtered_dishes = restaurant.dish_set.filter(onsale=True)[:5]

        return context

'''
class RestaurantListView(generic.ListView):
    model = RESTAURANT
    template_name = 'catalog/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        location = self.request.GET.get('location')
        tag = self.request.GET.get('tag')
        # 使用ZoneInfo获取上海时区
        shanghai_timezone = ZoneInfo('Asia/Shanghai')
        current_time = timezone.now().astimezone(shanghai_timezone)
        # Filter by current time within time_open and time_close
        queryset = queryset.filter(
            Q(time_open__lte=current_time, time_close__gte=current_time) |
            Q(time_open__isnull=True) | Q(time_close__isnull=True)
        )
        if search_query:
            queryset = queryset.filter(
                Q(resta_name__icontains=search_query) |
                Q(dish__dish_name__icontains=search_query)
            ).distinct()
        queryset = queryset.order_by('-AVG_grade')
        if location:
            queryset = queryset.filter(location=location)
        if tag:
            queryset = queryset.filter(tag=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['location'] = self.request.GET.get('location', '')
        context['location_choices'] = RESTAURANT.location_choice
        context['tag'] = self.request.GET.get('tag', '')
        context['tag_choices'] = RESTAURANT.tag_choice
        # Adding filtered dishes to each restaurant
        search_query = self.request.GET.get('q', '')
        if search_query:
            for restaurant in context['restaurants']:
                restaurant.filtered_dishes = restaurant.dish_set.filter(dish_name__icontains=search_query,onsale=True)
        else:
            for restaurant in context['restaurants']:
                restaurant.filtered_dishes = restaurant.dish_set.filter(onsale=True)

        
        return context
'''
class DishListView(generic.ListView):
    model = DISH

class RestaurantDetailView(generic.DetailView):
    model = RESTAURANT
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取相关信息
        context['restaurant_dishes'] = DISH.objects.filter(resta_ID=self.object.resta_ID, onsale=True)
        context['restaurant_comments_and_replies'] = COMMENT.objects.filter(resta_ID = self.object.resta_ID).prefetch_related('replies')
        # 添加用户权限信息到上下文
        restaurant = self.get_object()
        context['can_edit'] = restaurant.manager is None or self.request.user == restaurant.manager
        return context

    def test_func(self):
        restaurant = self.get_object()
        if restaurant.manager is None:
            return self.request.user.is_authenticated
        return self.request.user == restaurant.manager    

class DishDetailView(generic.DetailView):
    model = DISH

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取相关信息
        context['dish_comments_and_replies'] = COMMENT.objects.filter(dish_ID = self.object.dish_ID).prefetch_related('replies')
        dish = self.get_object()
        context['can_edit'] = dish.resta_ID.manager is None or self.request.user == dish.resta_ID.manager
        return context
    def test_func(self):
        restaurant = self.get_object()
        if restaurant.manager is None:
            return self.request.user.is_authenticated
        return self.request.user == restaurant.manager
# # 导入模块
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout

def register(request):
	if request.method == 'GET':
		return render(
			request,
			'registration/register.html'
		)
	
	elif request.method == 'POST':
		# 获取参数
		user_name = request.POST.get('username')
		pwd = request.POST.get('password')
		
		if not user_name or not pwd:
			return render(request, 'registration/register.html', {'errors': ['请将信息填写完整']})
			

		# 用户已存在
		if User.objects.filter(username=user_name):
			return render(request, 'registration/register.html', {'errors': ['该昵称已存在，请换一个昵称']})
		else:
			# 使用User内置方法创建用户
			user = User.objects.create_user(
				username=user_name,
				password=pwd,
				email='123@qq.com',
				is_staff=0,
				is_active=1,
				is_superuser=0
			)
			user.save()
			
			return redirect('restaurants')
	
	else:
		return render(
			request,
			'registration/register.html'
		)
	

from django.urls import reverse
@login_required
def adddishes_form(request):
    if request.method == 'POST':
        resta_ID = request.POST.get('resta_ID')
        # 重定向到表单页面并传递主码
        return redirect(reverse('adddishes') + f'?resta_ID={resta_ID}')
    return render(request, 'catalog/restaurant_detail.html')
@login_required
def adddishes(request):
    if request.method == 'POST':
        resta_ID = request.POST.get('resta_ID')
        dish_name = request.POST.get('dishname')
        price_c = request.POST.get('price')
        more_Info = request.POST.get('moreinfo')
        image = request.FILES.get('image')

        # 处理表单数据
        if not resta_ID or not dish_name:
            return render(request, 'catalog/add_dishes.html', {'errors': ['餐厅与菜名必填']})
        if not image:
             image = 'dishes/404.png'

        # 菜品已存在
        if DISH.objects.filter(resta_ID=resta_ID, dish_name=dish_name).exists():
            return render(request, 'catalog/add_dishes.html', {'errors': ['菜品已存在']})

        restaurant = RESTAURANT.objects.get(resta_ID=resta_ID)

        # 权限检查
        if restaurant.manager is not None and request.user != restaurant.manager:
            raise PermissionDenied

        # 尝试保存新菜品
        if 1:
            restaurant = RESTAURANT.objects.get(resta_ID=resta_ID)
            price = float(price_c) if price_c else None

            dish = DISH(
                resta_ID=restaurant,
                dish_name=dish_name,
                price=price,
                more_Info=more_Info,
                image=image
            )
            dish.full_clean()  # 验证字段
            dish.save()
            return redirect('restaurant-detail', pk=resta_ID)  # 重定向到餐馆详情页面

    else:
        resta_ID = request.GET.get('resta_ID')
        return render(request, 'catalog/add_dishes.html', {'resta_ID': resta_ID})


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import RESTAURANT
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import RESTAURANT


@login_required
def editrestaurants(request, pk):
    restaurant = get_object_or_404(RESTAURANT, pk=pk)
    location_choices = RESTAURANT.location_choice
    if request.method == 'POST':
        resta_name = request.POST.get('resta_name')
        location = request.POST.get('location')
        time_open = request.POST.get('time_open')
        time_close = request.POST.get('time_close')
        tag = request.POST.get('tag')
        more_Info = request.POST.get('more_Info')
        image = request.FILES.get('image') if 'image' in request.FILES else None
        isopen = request.POST.get('isopen') == 'on'

        restaurant = RESTAURANT.objects.get(resta_ID=pk)

        # 权限检查
        if restaurant.manager is not None and request.user != restaurant.manager:
            raise PermissionDenied
        # 更新餐厅信息
        restaurant.resta_name = resta_name
        restaurant.location = location
        restaurant.time_open = time_open
        restaurant.time_close = time_close
        restaurant.tag = tag
        restaurant.more_Info = more_Info
        if image:
            restaurant.image = image
        restaurant.isopen = isopen

        try:
            restaurant.full_clean()  # 验证字段
            restaurant.save()
            return redirect('restaurant-detail', pk=restaurant.resta_ID)
        except ValidationError as e:
            print(f'ERROR: Validation error - {e}')
            return render(request, "edit_restaurants.html", {'restaurant': restaurant, 'errors': e.messages, 'location_choices': location_choices})
        except IntegrityError as e:
            print(f'ERROR: Integrity error - {e}')
            return render(request, "edit_restaurants.html", {'restaurant': restaurant, 'errors': [str(e)], 'location_choices': location_choices})
        except Exception as e:
            print(f'ERROR: {e}')
            return render(request, "edit_restaurants.html", {'restaurant': restaurant, 'errors': [str(e)], 'location_choices': location_choices})

    return render(request, 'catalog/edit_restaurants.html', {'restaurant': restaurant, 'location_choices': location_choices})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import RESTAURANT, DISH, COMMENT

@login_required
def add_comment(request, pk):
    restaurant = get_object_or_404(RESTAURANT, pk=pk)
    dishes = DISH.objects.filter(resta_ID=restaurant)

    if request.method == 'POST':
        grade = request.POST.get('grade')
        content = request.POST.get('content')
        dish_id = request.POST.get('dish_ID')

        # Check for valid inputs
        if not grade or not content:
            return render(request, 'catalog/add_comment.html', {'restaurant': restaurant, 'dishes': dishes, 'errors': ['评分与内容均不能为空']})

        # Create and save the comment
        comment = COMMENT(
            user_ID=request.user,
            resta_ID=restaurant,
            dish_ID=DISH.objects.get(pk=dish_id) if dish_id else None,
            grade=grade,
            content=content
        )
        comment.save()
        return redirect('restaurant-detail', pk=restaurant.pk)

    return render(request, 'catalog/add_comment.html', {'restaurant': restaurant, 'dishes': dishes})

@login_required
def add_reply(request, pk):
    comment = get_object_or_404(COMMENT, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')

        # Check for valid inputs
        if not content:
            return render(request, 'catalog/add_comment.html', {'comment': comment, 'errors': ['内容不能为空']})

        # Create and save the comment
        reply = REPLY(
            user_ID=request.user,
            comm_ID=comment,
            content=content
        )
        reply.save()
        return redirect('restaurant-detail', pk=comment.resta_ID.pk)

    return render(request, 'catalog/add_reply.html', {'comment': comment})

@login_required
def addrestaurant(request):
    """
    View function for renewing a specific BookInstance by librarian
    """

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        form = AddRestaurantForm(request.POST,request.FILES)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            form.save()  # 保存数据到数据库
            return redirect('index' )
            # redirect to a new URL:


    # If this is a GET (or any other method) create the default form.
    else:
        form = AddRestaurantForm
    return render(request, 'catalog/addrestaurant.html', {'form': form})


def managerlogin(request):
	if request.method == 'GET':
		return render(
			request,
			'registration/managerlogin.html'
		)

	elif request.method == 'POST':
		# 获取参数
		user_name = request.POST.get('username')
		pwd = request.POST.get('password')

		if not user_name or not pwd:
			return render(request, 'registration/managerlogin.html', {'errors': ['请将信息填写完整']})

		# 用户不存在
		if not User.objects.filter(username=user_name):
			return render(request, 'registration/managerlogin.html', {'errors': ['用户不存在']})

		# 用户存在但非经理
		for auser in User.objects.filter(username=user_name):
			if auser.is_staff == 0:
				return render(request, 'registration/managerlogin.html', {'errors': ['您不是经理']})

        # 认证
		user = authenticate(request, username=user_name, password=pwd)
		if user is not None:
			login(request, user)
            # Redirect to a success page.
			return redirect('restaurants')
		else:
			return render(request, 'registration/managerlogin.html', {'errors': ['密码错误']})
	else:
		return render(request, "login_fail.html")


@login_required
def editdishes(request, pk):
    dish = get_object_or_404(DISH, pk=pk)
    if request.method == 'POST':
        dish_name = request.POST.get('dish_name')
        price_c = request.POST.get('price')
        more_Info = request.POST.get('moreinfo')
        image = request.FILES.get('image')

        dish = DISH.objects.get(dish_ID=pk)

        # 权限检查
        if dish.resta_ID.manager is not None and request.user != dish.resta_ID.manager:
            raise PermissionDenied

        # 更新餐厅信息
        dish.dish_name = dish_name
        dish.price = price_c
        dish.more_Info = more_Info
        if image:
            dish.image = image

        try:
            dish.full_clean()  # 验证字段
            dish.save()
            return redirect('dish-detail', pk=dish.dish_ID)
        except ValidationError as e:
            print(f'ERROR: Validation error - {e}')
            return render(request, "catalog/edit_dishes.html", {'dish': dish, 'errors': e.messages})
        except IntegrityError as e:
            print(f'ERROR: Integrity error - {e}')
            return render(request, "catalog/edit_dishes.html", {'dish': dish, 'errors': [str(e)]})
        except Exception as e:
            print(f'ERROR: {e}')
            return render(request, "catalog/edit_dishes.html", {'dish': dish, 'errors': [str(e)]})

    return render(request, 'catalog/edit_dishes.html', {'dish': dish})


@login_required
def add_comment_dish(request, pk):
    dish = get_object_or_404(DISH, pk=pk)

    if request.method == 'POST':
        grade = request.POST.get('grade')
        content = request.POST.get('content')

        # Check for valid inputs
        if not grade or not content:
            return render(request, 'catalog/add_comment_dish.html', {'dish': dish, 'errors': ['评分与内容均不能为空']})

        # Create and save the comment
        comment = COMMENT(
            user_ID=request.user,
            resta_ID=dish.resta_ID,
            dish_ID=dish,
            grade=grade,
            content=content
        )
        comment.save()
        return redirect('dish-detail', pk=dish.pk)

    return render(request, 'catalog/add_comment_dish.html', {'dish': dish})


@login_required
def add_reply_dish(request, pk):
    comment = get_object_or_404(COMMENT, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')

        # Check for valid inputs
        if not content:
            return render(request, 'catalog/add_reply.html', {'comment': comment, 'errors': ['内容不能为空']})

        # Create and save the comment
        reply = REPLY(
            user_ID=request.user,
            comm_ID=comment,
            content=content
        )
        reply.save()
        return redirect('dish-detail', pk=comment.dish_ID.pk)

    return render(request, 'catalog/add_reply.html', {'comment': comment})


@login_required
def deleterestaurants(request, pk):
    restaurant = get_object_or_404(RESTAURANT, pk=pk)
    if request.method == 'POST':
        image = request.FILES.get('image')

        # 图片不能为空
        if not image:
            return render(request, "login_fail.html", {'errors': ['证据不能为空']})

        # 更新餐厅信息
        delete_Info = DELETE_RESTA(
             resta_ID = restaurant,
             evidence = image
        )
        try:
            delete_Info.full_clean()  # 验证字段
            delete_Info.save()
            return redirect('restaurant-detail', pk=pk)
        except ValidationError as e:
            print(f'ERROR: Validation error - {e}')
            return render(request, "catalog/delete_restaurants.html", {'restaurant': restaurant, 'errors': e.messages})
        except IntegrityError as e:
            print(f'ERROR: Integrity error - {e}')
            return render(request, "catalog/delete_restaurants.html", {'restaurant': restaurant, 'errors': [str(e)]})
        except Exception as e:
            print(f'ERROR: {e}')
            return render(request, "catalog/delete_restaurants.html", {'restaurant': restaurant, 'errors': [str(e)]})

    return render(request, 'catalog/delete_restaurants.html', {'restaurant': restaurant})


@login_required
def deletedishes(request, pk):
    if request.method == 'POST':
        dish = get_object_or_404(DISH, pk=pk)
        dish.onsale = False
        dish.full_clean()  # 验证字段
        dish.save()
        return redirect('restaurant-detail', pk=dish.resta_ID.pk)
    '''
        except ValidationError as e:
            print(f'ERROR: Validation error - {e}')
            return redirect('dish-detail', pk=pk)
        except IntegrityError as e:
            print(f'ERROR: Integrity error - {e}')
            return redirect('dish-detail', pk=pk)
        except Exception as e:
            print(f'ERROR: {e}')
            return redirect('dish-detail', pk=pk)
    '''
    return redirect('deletedishes', pk=pk)


def register_manager(request):
	if request.method == 'GET':
		return render(
			request,
			'registration/register_manager.html'
		)

	elif request.method == 'POST':
		# 获取参数
		user_name = request.POST.get('username')
		pwd = request.POST.get('password')

		if not user_name or not pwd:
			return render(request, 'registration/register_manager.html', {'errors': ['请将信息填写完整']})

		# 用户已存在
		if User.objects.filter(username=user_name):
			return render(request, 'registration/register_manager.html', {'errors': ['该昵称已存在，请换一个昵称']})

        # 用户不存在
		else:
			# 使用User内置方法创建用户
			user = User.objects.create_user(
				username=user_name,
				password=pwd,
				email='123@qq.com',
				is_staff=1,
				is_active=1,
				is_superuser=0
			)
			user.save()

			return redirect('restaurants')

	else:
		return render(
			request,
			'registration/register_manager.html'
		)

def adddish(request):

    if request.method == 'POST':
        form = AddDish(request.POST,request.FILES)
        if form.is_valid():
            form.save()  
            return redirect('index' )
    else:
        form = AddDish
    return render(request, 'catalog/adddish.html', {'form': form})
@login_required
def manager(request, pk):
    manager = get_object_or_404(User, pk=pk)
    # 检查当前用户是否是指定的manager
    if request.user != manager:
        # 渲染自定义的403页面
        return render(request, 'catalog/403.html')
    restaurants = RESTAURANT.objects.filter(manager=manager)
    context = {
        'manager': manager,
        'restaurants': restaurants
    }
    return render(request, 'catalog/manager.html', context)

@login_required
def applyrestaurant(request):
    if request.method == 'POST':
        form = ApplyRestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            manager_reg = form.save(commit=False)
            manager_reg.user_ID = request.user  # 设置 user_ID 为当前登录用户
            manager_reg.save()
            return redirect('index' )
    else:
        form = ApplyRestaurantForm()
    return render(request, 'catalog/applyrestaurant.html', {'form': form})