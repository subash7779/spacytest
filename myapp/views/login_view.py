from django.shortcuts import render, redirect
from django.contrib import messages
from myapp import credentials

class User:
    def __init__(self, username, password, usertype):
        self.username = username
        self.password = password
        self.usertype = usertype
        
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        for user in credentials.USERS:
            if user["username"] == username and user["password"] == password:
                user_obj = User(**user)
                request.session['username'] = username
                request.session['usertype'] = user_obj.usertype
                return redirect('/dashboard')
        
        messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    if 'username' in request.session:
        del request.session['username']
    if 'usertype' in request.session:
        del request.session['usertype']
    return redirect('user_login')