from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from models.user import db
from models.student_profile import StudentProfile
from models.company_profile import CompanyProfile
from models.opportunity import Opportunity
from models.application import Application
from utils import role_required


student = Blueprint(
    "student",
    __name__,
    url_prefix="/student"
)


# =========================
# STUDENT DASHBOARD
# =========================

@student.route("/dashboard")
@login_required
@role_required("student")
def dashboard():

    return render_template(
        "student/dashboard.html",
        user=current_user
    )


# =========================
# STUDENT PROFILE
# =========================

@student.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("student")
def profile():

    profile = StudentProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":

        matric_number = request.form["matric_number"]
        phone = request.form["phone"]
        university = request.form["university"]
        faculty = request.form["faculty"]
        department = request.form["department"]
        programme = request.form["programme"]
        level = request.form["level"]
        cgpa = request.form["cgpa"]
        skills = request.form["skills"]
        preferred_state = request.form["preferred_state"]
        preferred_city = request.form["preferred_city"]

        if profile is None:

            profile = StudentProfile(
                user_id=current_user.id
            )

            db.session.add(profile)

        profile.matric_number = matric_number
        profile.phone = phone
        profile.university = university
        profile.faculty = faculty
        profile.department = department
        profile.programme = programme
        profile.level = level

        if cgpa:
            profile.cgpa = float(cgpa)
        else:
            profile.cgpa = None

        profile.skills = skills
        profile.preferred_state = preferred_state
        profile.preferred_city = preferred_city

        db.session.commit()

        flash("Your profile has been saved successfully.")

        return redirect(
            url_for("student.profile")
        )

    return render_template(
        "student/profile.html",
        profile=profile,
        user=current_user
    )


# =========================
# STUDENT OPPORTUNITIES
# =========================

@student.route("/opportunities")
@login_required
@role_required("student")
def opportunities():

    opportunities = Opportunity.query.order_by(
        Opportunity.created_at.desc()
    ).all()

    # Get applications made by this student
    applications = Application.query.filter_by(
        student_id=current_user.id
    ).all()

    # Store opportunity IDs already applied for
    applied_ids = {
        application.opportunity_id
        for application in applications
    }

    return render_template(
        "student/opportunities.html",
        opportunities=opportunities,
        applied_ids=applied_ids,
        user=current_user
    )


# =========================
# APPLY FOR OPPORTUNITY
# =========================

@student.route(
    "/opportunity/<int:opportunity_id>/apply",
    methods=["POST"]
)
@login_required
@role_required("student")
def apply(opportunity_id):

    opportunity = Opportunity.query.get_or_404(
        opportunity_id
    )

    # Check if student has already applied
    existing_application = Application.query.filter_by(
        student_id=current_user.id,
        opportunity_id=opportunity.id
    ).first()

    if existing_application:

        flash(
            "You have already applied for this opportunity."
        )

        return redirect(
            url_for("student.opportunities")
        )

    # Create application
    application = Application(
        student_id=current_user.id,
        opportunity_id=opportunity.id,
        status="Pending"
    )

    db.session.add(application)
    db.session.commit()

    flash(
        "Application submitted successfully!"
    )

    return redirect(
        url_for("student.applications")
    )


# =========================
# STUDENT MY APPLICATIONS
# =========================

@student.route("/applications")
@login_required
@role_required("student")
def applications():

    applications = (
        Application.query
        .filter_by(
            student_id=current_user.id
        )
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )

    return render_template(
        "student/applications.html",
        applications=applications,
        user=current_user
    )


# =========================
# STUDENT MY PLACEMENT
# =========================

@student.route("/placement")
@login_required
@role_required("student")
def placement():

    accepted_applications = (
        Application.query
        .filter_by(
            student_id=current_user.id,
            status="Accepted"
        )
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )

    # Get the company profile for each accepted placement
    placement_companies = {}

    for application in accepted_applications:

        company_profile = CompanyProfile.query.filter_by(
            user_id=application.opportunity.company_id
        ).first()

        placement_companies[application.id] = company_profile

    return render_template(
        "student/placement.html",
        accepted_applications=accepted_applications,
        placement_companies=placement_companies,
        user=current_user
    )


# =========================
# SET PLACEMENT DATES
# =========================

@student.route(
    "/placement/<int:application_id>/dates",
    methods=["POST"]
)
@login_required
@role_required("student")
def set_placement_dates(application_id):

    application = Application.query.get_or_404(application_id)

    # Make sure this placement belongs to the logged-in student
    if application.student_id != current_user.id:

        flash("You are not authorized to edit this placement.")

        return redirect(url_for("student.placement"))

    if application.status != "Accepted":

        flash("You can only set dates for an accepted placement.")

        return redirect(url_for("student.placement"))

    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")

    if start_date_str:
        application.start_date = datetime.strptime(
            start_date_str, "%Y-%m-%d"
        ).date()

    if end_date_str:
        application.end_date = datetime.strptime(
            end_date_str, "%Y-%m-%d"
        ).date()

    if (
        application.start_date
        and application.end_date
        and application.end_date < application.start_date
    ):

        flash("End date cannot be before the start date.")

        return redirect(url_for("student.placement"))

    db.session.commit()

    flash("Placement dates saved successfully.")

    return redirect(url_for("student.placement"))