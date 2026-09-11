from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models.user import db, User
from models.student_profile import StudentProfile
from models.company_profile import CompanyProfile
from models.opportunity import Opportunity
from models.application import Application
from utils import role_required


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =========================
# ADMIN DASHBOARD
# =========================

@admin.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():

    stats = {
        "total_students": User.query.filter_by(role="student").count(),
        "total_companies": User.query.filter_by(role="company").count(),
        "pending_companies": User.query.filter_by(
            role="company", is_approved=False
        ).count(),
        "total_opportunities": Opportunity.query.count(),
        "total_applications": Application.query.count(),
        "students_placed": Application.query.filter_by(
            status="Accepted"
        ).count(),
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        user=current_user
    )


# =========================
# MANAGE COMPANIES
# =========================

@admin.route("/companies")
@login_required
@role_required("admin")
def companies():

    company_users = User.query.filter_by(role="company").order_by(
        User.id.desc()
    ).all()

    company_profiles = {}

    for company_user in company_users:

        profile = CompanyProfile.query.filter_by(
            user_id=company_user.id
        ).first()

        company_profiles[company_user.id] = profile

    return render_template(
        "admin/companies.html",
        company_users=company_users,
        company_profiles=company_profiles,
        user=current_user
    )


@admin.route("/company/<int:user_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def approve_company(user_id):

    company_user = User.query.get_or_404(user_id)

    company_user.is_approved = True

    db.session.commit()

    flash(f"{company_user.full_name} has been approved.")

    return redirect(url_for("admin.companies"))


@admin.route("/company/<int:user_id>/suspend", methods=["POST"])
@login_required
@role_required("admin")
def suspend_company(user_id):

    company_user = User.query.get_or_404(user_id)

    company_user.is_approved = False

    db.session.commit()

    flash(f"{company_user.full_name} has been suspended.")

    return redirect(url_for("admin.companies"))


# =========================
# MANAGE STUDENTS
# =========================

@admin.route("/students")
@login_required
@role_required("admin")
def students():

    student_users = User.query.filter_by(role="student").order_by(
        User.id.desc()
    ).all()

    student_profiles = {}

    for student_user in student_users:

        profile = StudentProfile.query.filter_by(
            user_id=student_user.id
        ).first()

        student_profiles[student_user.id] = profile

    return render_template(
        "admin/students.html",
        student_users=student_users,
        student_profiles=student_profiles,
        user=current_user
    )


# =========================
# MANAGE OPPORTUNITIES
# =========================

@admin.route("/opportunities")
@login_required
@role_required("admin")
def opportunities():

    all_opportunities = Opportunity.query.order_by(
        Opportunity.created_at.desc()
    ).all()

    return render_template(
        "admin/opportunities.html",
        opportunities=all_opportunities,
        user=current_user
    )


@admin.route(
    "/opportunity/<int:opportunity_id>/delete",
    methods=["POST"]
)
@login_required
@role_required("admin")
def delete_opportunity(opportunity_id):

    opportunity = Opportunity.query.get_or_404(opportunity_id)

    db.session.delete(opportunity)
    db.session.commit()

    flash("Opportunity removed.")

    return redirect(url_for("admin.opportunities"))