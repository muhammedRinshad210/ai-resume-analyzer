from django.shortcuts import render

import PyPDF2

from .models import Resume
# Create your views here.


def index(request):
    
     # 🔐 AUTH CHECK FIRST
    if not request.user.is_authenticated:
        return redirect("login")
    
    feedback = []
    data = Resume.objects.filter(user = request.user)
    
    if request.method == "POST":

        # DELETE FUNCTION
        if 'delete_id' in request.POST:
            Resume.objects.filter(id=request.POST['delete_id']).delete()
            return render(request, "home.html", { 
                "feedback" : ["🗑️ Resume deleted"],
                "data" : Resume.objects.filter(user = request.user)
            })
        

        # search
        elif 'search' in request.POST:
            query = request.POST.get('search')

            data = Resume.objects.filter(
                name__icontains=query
            ) | Resume.objects.filter(
                skills__icontains=query
            )

            return render(request, "home.html", {
                "feedback" : [f"🔍 Result of '{query}'"],
                "data" : Resume.objects.filter(user = request.user)
            })
        

        # edit
        elif 'edit_id' in request.POST:
            edit_data = Resume.objects.get(id = request.POST['edit_id'])

            return render(request, "home.html", {
                "edit_data" : edit_data,
                "data" : Resume.objects.filter(user = request.user)
            })
        
        # update
        elif 'update_id' in request.POST:
            update_id = request.POST.get('update_id')

            # 🛑 FIX: check empty id
            if not update_id:
                feedback.append("❌ No items selected for update")

                return render(request, "home.html", {
                    "feedback" : feedback,
                    "data" : Resume.objects.filter(user = request.user)
                })

            obj = Resume.objects.filter(id = update_id).first()

            if not obj:
                feedback.append("❌ Resume not found")
            else:
                obj.name = request.POST.get('name')
                obj.skills = request.POST.get('skills')
                obj.save()

                feedback.append("✏️ Resume updated")

            
            

        # UPLOAD
        else:
            file = request.FILES.get('resume')

            # not uploading no error
            if not file:
                feedback.append("❌ No file uploaded")
                return render(request, "home.html", {
                    "feedback": feedback,
                    "data": data
                    })


            print(file.name)
            reader = PyPDF2.PdfReader(file)
            # reader.pages
            text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content
                # text += page.extract_text()  #single line
            print(text)
        
            if len(text) < 300:
                feedback.append("❌ Resume too short")
            else:
                feedback.append("✅ Good length")

            print(feedback)

            skills = ["python","django","html","css","javascript"]
            text = text.lower()

            found = []

            for skill in skills:
                if skill in text:
                    found.append(skill)

            if found:
                feedback.append("✅ Skills found: " + ", ".join(found))
            else:
                feedback.append("❌ No Skills found")

            print(found)

            Resume.objects.create(
                user = request.user,
                name = file.name,
                skills = ", ".join(found)
            )

            Resume.objects.filter(user=request.user)
        

    return render(request, "home.html", {
        "feedback": feedback, 
        "data" : data
        })







from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

# login 

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {
                "error" : "Invalid credentials"
            })
        
    return render(request, "login.html")


# logout 
def logout_view(request):
    logout(request)
    return redirect("login")



# Uer page 
from django.contrib.auth.models import User


def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            return render(request, "signup.html" , {
                "error" : "password donot match"
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error" : "username alresy exists"
            })
        
        user = User.objects.create_user(
            username = username,
            password = password
        )

        login(request, user)

        return redirect("index")
        
    return render(request, "signup.html")