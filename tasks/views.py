from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.

#Renderiza la vista de la pagina principal
def home(request):
    return render(request, 'home.html')


#renderiza la vista de la pagina de registro de usuario, implementa el formulario de registro de usuarios que nos ofrece Django
def register(request):
    
    #valida si el metodo que se recibe HTTP es GET renderiza el formulario
    if request.method == 'GET':
        return render(request, 'register.html',{
            'form' : UserCreationForm
        })
    else:
        # caso contrario si el metodo es POST recibe y valida primeramente que el password si coincida.
        if request.POST['password1'] == request.POST['password2']:
            
            #si coincide el password entonces intenta crear un objeto usuario tomando desde el request el username y el password, si todo sale bien, guarda el usuario en la BD, crea un sesionID y redirije al pagina tasks.html
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                # caso contrario si hubo un error de integridad, entonces retorna nuevamente el formulario con el error de integridad
                return render(request, 'register.html', {
                    'error' : 'user already exist',
                    'form' : UserCreationForm
                })
        # en caso de que los password no coincidan nuevamente renderiza el formulario y muestra el error de que los password no coinciden.        
        return render(request, 'register.html',{
            'error':'Password do not match',
            'form': UserCreationForm
        })


#renderiza la vista login.html
def signin(request):
    #validacion del request HTTP del navegador si es por el metodo GET renderiza el formulario
    if request.method == 'GET':
        return render(request, 'login.html',{
            'form':AuthenticationForm
        })
    else:
        #caso contrario algun otro metodo por ejemplo POST usa el metodo authenticate para validar si existe en la DB el usuario y password que vienen desde el request.POST y si existe logea la sesion y redirecciona a la vista de tareas, si no muestra un error.
         
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'login.html',{
                'form':AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')
        
# renderiza la vista tasks.html
@login_required
def tasks(request):
    # hacinedo uso del modelo Task de la BD hacemos una consulta filtrando por usuario y diciendo si el dato fecha_completada aun no esta marcada.
    tasks = Task.objects.filter(user=request.user, fecha_completada__isnull=True)
    return render(request,'tasks.html',{'tasks':tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, fecha_completada__isnull=False).order_by('-fecha_completada')
    return render(request, 'tasks.html',{'tasks':tasks})

@login_required
def create_task(request):
    
    # si el request del navegador HTTP es el metodo GET renderiza el formulario 
    if request.method == 'GET':
        return render(request, 'create_task.html',{
            'form': TaskForm
        })
    #caso contrario intenta guardar los datos del formulario en una nueva tarea y si no hay error redirecciona a la pagina Tasks.html
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html',{
                'form': TaskForm,
                'error': 'Por favor ingresa un tipo de dato valido'
            })
            

@login_required
def task_detail(request,task_id):
    #rendeeriza el detalle de la tarea mediante una consulta y si no se encuentra ese ID, envia un error 404 en lugar de tumbar el servidor por un error en la consulta
    
    # Si el metodo HTTP que recibe del navegador es GET crea la vista de la tarea seleccionada y le da el formulario para actualizar
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html',{'task':task,'form':form})        
    else:
    # Si esta actualizando los datos, los toma, y guarda el formluario, despues redirige a la pantalla Tasks
        try:
            task = get_object_or_404(Task,pk=task_id, user=request.user)
            form = TaskForm(request.POST,instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html',{'task':task,'form':form,'error':'Error al actualizar la Tarea'})
        
            
@login_required
def complete_task(request,task_id):
    # para completar la terea hacemos uso de la consulta get object or 404 y le pasamos que del modelo tarea filtre con el primary key de la tarea, y que tambien filtre por el usuario que sea igual al usuario que le estamos pasando despues usamos el metodo timezone.now() para actualizar la propiedad fecha_completada y guardamos ese valor, posteriormente redirecccionamos
    task = get_object_or_404(Task,pk=task_id, user=request.user)
    if request.method == 'POST':
        task.fecha_completada = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    #Es practicamente lo mismo que la funcion complete, solo que en este caso usamos el metodo delete en lugar del save. 
    task = get_object_or_404(Task, pk= task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

def signout(request):
    logout(request)
    return redirect('home')