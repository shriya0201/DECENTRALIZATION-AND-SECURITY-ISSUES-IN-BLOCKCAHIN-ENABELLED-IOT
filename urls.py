from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path("CreateProfile.html", views.CreateProfile, name="CreateProfile"),
	       path("CreateProfileData", views.CreateProfileData, name="CreateProfileData"),
	       path("Agency.html", views.Agency, name="Agency"),
	       path("AgencyLogin", views.AgencyLogin, name="AgencyLogin"),
	       path("AccessData.html", views.AccessData, name="AccessData"),
	       path("PatientDataAccess", views.PatientDataAccess, name="PatientDataAccess"),
	       path("Patient.html", views.Patient, name="Patient"),
	       path("PatientLogin", views.PatientLogin, name="PatientLogin"),
	       path("AgencySignup.html", views.AgencySignup, name="AgencySignup"),
	       path("AgencySignupAction", views.AgencySignupAction, name="AgencySignupAction"),
]