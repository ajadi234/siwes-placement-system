from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models.user import db, User
from models.company_profile import CompanyProfile
from models.student_profile import StudentProfile
from models.opportunity import Opportunity
from models.application import Application
from utils import role_required


company = Blueprint(
    "company",
    __name__,
    url_prefix="/company"
)


# =========================
# COMPANY DASHBOARD
# =========================

@company.route("/dashboard")
@login_required
@role_required("company")
def dashboard():

    return render_template(
        "company/dashboard.html",
        user=current_user
    )


# =========================
# COMPANY PROFILE
# =========================

@company.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("company")
def profile():

    profile = CompanyProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":

        organization_name = request.form["organization_name"]
        organization_type = request.form["organization_type"]
        phone = request.form["phone"]
        address = request.form["address"]
        state = request.form["state"]
        city = request.form["city"]
        website = request.form["website"]
        contact_person = request.form["contact_person"]
        description = request.form["description"]

        if profile is None:

            profile = CompanyProfile(
                user_id=current_user.id
            )

            db.session.add(profile)

        profile.organization_name = organization_name
        profile.organization_type = organization_type
        profile.phone = phone
        profile.address = address
        profile.state = state
        profile.city = city
        profile.website = website
        profile.contact_person = contact_person
        profile.description = description

        db.session.commit()

        flash("Company profile saved successfully.")

        return redirect(
            url_for("company.profile")
        )

    return render_template(
        "company/profile.html",
        profile=profile,
        user=current_user
    )


# =========================
# CREATE OPPORTUNITY
# =========================

@company.route("/opportunity/new", methods=["GET", "POST"])
@login_required
@role_required("company")
def create_opportunity():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        requirements = request.form["requirements"]
        location = request.form["location"]
        state = request.form["state"]
        city = request.form["city"]
        duration = request.form["duration"]
        opportunity_type = request.form["opportunity_type"]
        application_deadline = request.form["application_deadline"]

        opportunity = Opportunity(
            company_id=current_user.id,
            title=title,
            description=description,
            requirements=requirements,
            location=location,
            state=state,
            city=city,
            duration=duration,
            opportunity_type=opportunity_type,
            application_deadline=application_deadline
        )

        db.session.add(opportunity)

        db.session.commit()

        flash("Opportunity posted successfully!")

        return redirect(
            url_for("company.dashboard")
        )

    return render_template(
        "company/create_opportunity.html"
    )


# =========================
# COMPANY APPLICATIONS
# =========================

@company.route("/applications")
@login_required
@role_required("company")
def applications():

    applications = (
        Application.query
        .join(
            Opportunity,
            Application.opportunity_id == Opportunity.id
        )
        .filter(
            Opportunity.company_id == current_user.id
        )
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )

    # Get each student's profile
    application_profiles = {}

    for application in applications:

        profile = StudentProfile.query.filter_by(
            user_id=application.student_id
        ).first()

        application_profiles[application.id] = profile

    return render_template(
        "company/applications.html",
        applications=applications,
        application_profiles=application_profiles,
        user=current_user
    )


# =========================
# ACCEPT APPLICATION
# =========================

@company.route(
    "/application/<int:application_id>/accept",
    methods=["POST"]
)
@login_required
@role_required("company")
def accept_application(application_id):

    application = Application.query.get_or_404(
        application_id
    )

    # Make sure this application belongs
    # to an opportunity owned by this company
    if application.opportunity.company_id != current_user.id:

        flash(
            "You are not authorized to manage this application."
        )

        return redirect(
            url_for("company.applications")
        )

    application.status = "Accepted"

    db.session.commit()

    flash(
        "Application accepted successfully."
    )

    return redirect(
        url_for("company.applications")
    )


# =========================
# REJECT APPLICATION
# =========================

@company.route(
    "/application/<int:application_id>/reject",
    methods=["POST"]
)
@login_required
@role_required("company")
def reject_application(application_id):

    application = Application.query.get_or_404(
        application_id
    )

    # Make sure this application belongs
    # to an opportunity owned by this company
    if application.opportunity.company_id != current_user.id:

        flash(
            "You are not authorized to manage this application."
        )

        return redirect(
            url_for("company.applications")
        )

    application.status = "Rejected"

    db.session.commit()

    flash(
        "Application rejected."
    )

    return redirect(
        url_for("company.applications")
    )


# =========================
# COMPANY STUDENTS (ACCEPTED / PLACED)
# =========================

@company.route("/students")
@login_required
@role_required("company")
def students():

    placed_applications = (
        Application.query
        .join(
            Opportunity,
            Application.opportunity_id == Opportunity.id
        )
        .filter(
            Opportunity.company_id == current_user.id,
            Application.status == "Accepted"
        )
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )

    # Get each student's profile
    student_profiles = {}

    for application in placed_applications:

        profile = StudentProfile.query.filter_by(
            user_id=application.student_id
        ).first()

        student_profiles[application.id] = profile

    return render_template(
        "company/students.html",
        placed_applications=placed_applications,
        student_profiles=student_profiles,
        user=current_user
    )