from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Computed, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('email_change_confirm_status >= 0 AND email_change_confirm_status <= 2', name='users_email_change_confirm_status_check'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('phone', name='users_phone_key'),
        Index('confirmation_token_idx', 'confirmation_token', unique=True),
        Index('email_change_token_current_idx', 'email_change_token_current', unique=True),
        Index('email_change_token_new_idx', 'email_change_token_new', unique=True),
        Index('reauthentication_token_idx', 'reauthentication_token', unique=True),
        Index('recovery_token_idx', 'recovery_token', unique=True),
        Index('users_email_partial_key', 'email', unique=True),
        Index('users_instance_id_email_idx', 'instance_id'),
        Index('users_instance_id_idx', 'instance_id'),
        Index('users_is_anonymous_idx', 'is_anonymous'),
        {'comment': 'Auth: Stores user login data within a secure schema.',
     'schema': 'auth'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    is_sso_user: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.')
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    aud: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    encrypted_password: Mapped[Optional[str]] = mapped_column(String(255))
    email_confirmed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    invited_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    confirmation_token: Mapped[Optional[str]] = mapped_column(String(255))
    confirmation_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    recovery_token: Mapped[Optional[str]] = mapped_column(String(255))
    recovery_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    email_change_token_new: Mapped[Optional[str]] = mapped_column(String(255))
    email_change: Mapped[Optional[str]] = mapped_column(String(255))
    email_change_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_sign_in_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    raw_app_meta_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    raw_user_meta_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_super_admin: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    phone: Mapped[Optional[str]] = mapped_column(Text, server_default=text('NULL::character varying'))
    phone_confirmed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    phone_change: Mapped[Optional[str]] = mapped_column(Text, server_default=text("''::character varying"))
    phone_change_token: Mapped[Optional[str]] = mapped_column(String(255), server_default=text("''::character varying"))
    phone_change_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    confirmed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), Computed('LEAST(email_confirmed_at, phone_confirmed_at)', persisted=True))
    email_change_token_current: Mapped[Optional[str]] = mapped_column(String(255), server_default=text("''::character varying"))
    email_change_confirm_status: Mapped[Optional[int]] = mapped_column(SmallInteger, server_default=text('0'))
    banned_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    reauthentication_token: Mapped[Optional[str]] = mapped_column(String(255), server_default=text("''::character varying"))
    reauthentication_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='organizations_pkey'),
        UniqueConstraint('slug', name='organizations_slug_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    branding_config: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    profiles: Mapped[list['Profiles']] = relationship('Profiles', back_populates='organization')
    organization_members: Mapped[list['OrganizationMembers']] = relationship('OrganizationMembers', back_populates='organization')
    courses: Mapped[list['Courses']] = relationship('Courses', back_populates='organization')


class Skills(Base):
    __tablename__ = 'skills'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='skills_pkey'),
        UniqueConstraint('name', name='skills_name_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    name: Mapped[str] = mapped_column(Text, nullable=False)

    trainee: Mapped[list['TraineeProfiles']] = relationship('TraineeProfiles', secondary='public.trainee_skills', back_populates='skill')


class Profiles(Users):
    __tablename__ = 'profiles'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['auth.users.id'], ondelete='CASCADE', name='profiles_id_fkey'),
        ForeignKeyConstraint(['organization_id'], ['public.organizations.id'], name='profiles_organization_id_fkey'),
        PrimaryKeyConstraint('id', name='profiles_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    full_name: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    headline: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    xp_points: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    account_status: Mapped[Optional[str]] = mapped_column(Enum('UNVERIFIED', 'VERIFIED', 'REJECTED', name='account_status'), server_default=text("'UNVERIFIED'::account_status"))

    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='profiles')
    appointments: Mapped[list['Appointments']] = relationship('Appointments', foreign_keys='[Appointments.employer_id]', back_populates='employer')
    appointments_: Mapped[list['Appointments']] = relationship('Appointments', foreign_keys='[Appointments.trainee_id]', back_populates='trainee')
    employer_profiles: Mapped[Optional['EmployerProfiles']] = relationship('EmployerProfiles', uselist=False, back_populates='user')
    institution_profiles: Mapped[Optional['InstitutionProfiles']] = relationship('InstitutionProfiles', uselist=False, back_populates='user')
    messages: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.receiver_id]', back_populates='receiver')
    messages_: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.sender_id]', back_populates='sender')
    organization_members: Mapped[list['OrganizationMembers']] = relationship('OrganizationMembers', back_populates='user')
    trainee_profiles: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', uselist=False, back_populates='user')
    courses: Mapped[list['Courses']] = relationship('Courses', back_populates='instructor')
    certificates: Mapped[list['Certificates']] = relationship('Certificates', back_populates='user')
    class_streams: Mapped[list['ClassStreams']] = relationship('ClassStreams', back_populates='author')
    enrollments: Mapped[list['Enrollments']] = relationship('Enrollments', back_populates='user')
    assignment_submissions: Mapped[list['AssignmentSubmissions']] = relationship('AssignmentSubmissions', back_populates='user')
    stream_comments: Mapped[list['StreamComments']] = relationship('StreamComments', back_populates='user')
    code_executions: Mapped[list['CodeExecutions']] = relationship('CodeExecutions', back_populates='user')


class Appointments(Base):
    __tablename__ = 'appointments'
    __table_args__ = (
        ForeignKeyConstraint(['employer_id'], ['public.profiles.id'], name='appointments_employer_id_fkey'),
        ForeignKeyConstraint(['trainee_id'], ['public.profiles.id'], name='appointments_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='appointments_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    scheduled_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    employer_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    status: Mapped[Optional[str]] = mapped_column(Enum('PENDING', 'ACCEPTED', 'REJECTED', 'COMPLETED', 'CANCELLED', name='appointment_status'), server_default=text("'PENDING'::appointment_status"))
    note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    employer: Mapped[Optional['Profiles']] = relationship('Profiles', foreign_keys=[employer_id], back_populates='appointments')
    trainee: Mapped[Optional['Profiles']] = relationship('Profiles', foreign_keys=[trainee_id], back_populates='appointments_')


class EmployerProfiles(Base):
    __tablename__ = 'employer_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='employer_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='employer_profiles_pkey'),
        UniqueConstraint('user_id', name='employer_profiles_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    industry: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='employer_profiles')
    employer_invitations: Mapped[list['EmployerInvitations']] = relationship('EmployerInvitations', back_populates='employer')


class InstitutionProfiles(Base):
    __tablename__ = 'institution_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='institution_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='institution_profiles_pkey'),
        UniqueConstraint('user_id', name='institution_profiles_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    institution_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    institution_type: Mapped[Optional[str]] = mapped_column(Text)
    mission_vision: Mapped[Optional[str]] = mapped_column(Text)
    website_url: Mapped[Optional[str]] = mapped_column(Text)
    contact_email: Mapped[Optional[str]] = mapped_column(Text)
    contact_phone: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='institution_profiles')
    courses: Mapped[list['Courses']] = relationship('Courses', back_populates='institution')
    program_invitations: Mapped[list['ProgramInvitations']] = relationship('ProgramInvitations', back_populates='institution')


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        ForeignKeyConstraint(['receiver_id'], ['public.profiles.id'], ondelete='CASCADE', name='messages_receiver_id_fkey'),
        ForeignKeyConstraint(['sender_id'], ['public.profiles.id'], ondelete='CASCADE', name='messages_sender_id_fkey'),
        PrimaryKeyConstraint('id', name='messages_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    receiver_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    receiver: Mapped[Optional['Profiles']] = relationship('Profiles', foreign_keys=[receiver_id], back_populates='messages')
    sender: Mapped[Optional['Profiles']] = relationship('Profiles', foreign_keys=[sender_id], back_populates='messages_')


class OrganizationMembers(Base):
    __tablename__ = 'organization_members'
    __table_args__ = (
        ForeignKeyConstraint(['organization_id'], ['public.organizations.id'], ondelete='CASCADE', name='organization_members_organization_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='organization_members_user_id_fkey'),
        PrimaryKeyConstraint('id', name='organization_members_pkey'),
        UniqueConstraint('user_id', 'organization_id', name='organization_members_user_id_organization_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    role: Mapped[str] = mapped_column(Enum('trainee', 'instructor', 'ta', 'org_admin', 'super_admin', 'institution', 'employer', name='app_role'), nullable=False, server_default=text("'trainee'::app_role"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='organization_members')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='organization_members')


class TraineeProfiles(Base):
    __tablename__ = 'trainee_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='trainee_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='trainee_profiles_pkey'),
        UniqueConstraint('user_id', name='trainee_profiles_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    headline: Mapped[Optional[str]] = mapped_column(Text)
    cv_url: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(Text)
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    profile_complete: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    skill: Mapped[list['Skills']] = relationship('Skills', secondary='public.trainee_skills', back_populates='trainee')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='trainee_profiles')
    education: Mapped[list['Education']] = relationship('Education', back_populates='trainee')
    employer_invitations: Mapped[list['EmployerInvitations']] = relationship('EmployerInvitations', back_populates='trainee')
    experience: Mapped[list['Experience']] = relationship('Experience', back_populates='trainee')
    portfolio_projects: Mapped[list['PortfolioProjects']] = relationship('PortfolioProjects', back_populates='trainee')
    program_invitations: Mapped[list['ProgramInvitations']] = relationship('ProgramInvitations', back_populates='trainee')


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        ForeignKeyConstraint(['institution_id'], ['public.institution_profiles.id'], ondelete='CASCADE', name='courses_institution_id_fkey'),
        ForeignKeyConstraint(['instructor_id'], ['public.profiles.id'], ondelete='SET NULL', name='courses_instructor_id_fkey'),
        ForeignKeyConstraint(['organization_id'], ['public.organizations.id'], ondelete='CASCADE', name='courses_organization_id_fkey'),
        PrimaryKeyConstraint('id', name='courses_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    instructor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    subtitle: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    difficulty_level: Mapped[Optional[str]] = mapped_column(Enum('easy', 'medium', 'hard', name='difficulty_level'), server_default=text("'easy'::difficulty_level"))
    price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Enum('draft', 'pending_approval', 'published', 'archived', name='course_status'), server_default=text("'draft'::course_status"))
    is_featured: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    eligibility_criteria: Mapped[Optional[str]] = mapped_column(Text)
    learning_outcomes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    duration_info: Mapped[Optional[str]] = mapped_column(Text)

    institution: Mapped[Optional['InstitutionProfiles']] = relationship('InstitutionProfiles', back_populates='courses')
    instructor: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='courses')
    organization: Mapped[Optional['Organizations']] = relationship('Organizations', back_populates='courses')
    assessments: Mapped[list['Assessments']] = relationship('Assessments', back_populates='course')
    assignments: Mapped[list['Assignments']] = relationship('Assignments', back_populates='course')
    certificates: Mapped[list['Certificates']] = relationship('Certificates', back_populates='course')
    class_streams: Mapped[list['ClassStreams']] = relationship('ClassStreams', back_populates='course')
    enrollments: Mapped[list['Enrollments']] = relationship('Enrollments', back_populates='course')
    meetings: Mapped[list['Meetings']] = relationship('Meetings', back_populates='course')
    modules: Mapped[list['Modules']] = relationship('Modules', back_populates='course')
    program_invitations: Mapped[list['ProgramInvitations']] = relationship('ProgramInvitations', back_populates='course')


class Education(Base):
    __tablename__ = 'education'
    __table_args__ = (
        ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='CASCADE', name='education_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='education_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    institution_name: Mapped[str] = mapped_column(Text, nullable=False)
    qualification: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    field_of_study: Mapped[Optional[str]] = mapped_column(Text)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    trainee: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', back_populates='education')


class EmployerInvitations(Base):
    __tablename__ = 'employer_invitations'
    __table_args__ = (
        ForeignKeyConstraint(['employer_id'], ['public.employer_profiles.id'], ondelete='CASCADE', name='employer_invitations_employer_id_fkey'),
        ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='CASCADE', name='employer_invitations_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='employer_invitations_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    employer_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    message: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Enum('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='invitation_status'), server_default=text("'PENDING'::invitation_status"))
    appointment_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    employer: Mapped[Optional['EmployerProfiles']] = relationship('EmployerProfiles', back_populates='employer_invitations')
    trainee: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', back_populates='employer_invitations')


class Experience(Base):
    __tablename__ = 'experience'
    __table_args__ = (
        ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='CASCADE', name='experience_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='experience_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_current_role: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    trainee: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', back_populates='experience')


class PortfolioProjects(Base):
    __tablename__ = 'portfolio_projects'
    __table_args__ = (
        ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='CASCADE', name='portfolio_projects_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='portfolio_projects_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    project_url: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    trainee: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', back_populates='portfolio_projects')


t_trainee_skills = Table(
    'trainee_skills', Base.metadata,
    Column('trainee_id', Uuid, primary_key=True),
    Column('skill_id', Uuid, primary_key=True),
    ForeignKeyConstraint(['skill_id'], ['public.skills.id'], ondelete='CASCADE', name='trainee_skills_skill_id_fkey'),
    ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='CASCADE', name='trainee_skills_trainee_id_fkey'),
    PrimaryKeyConstraint('trainee_id', 'skill_id', name='trainee_skills_pkey'),
    schema='public'
)


class Assessments(Base):
    __tablename__ = 'assessments'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='assessments_course_id_fkey'),
        PrimaryKeyConstraint('id', name='assessments_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Enum('coding_challenge', 'quiz', 'timed_test', 'problem_solving', name='assessment_type'), nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty: Mapped[Optional[str]] = mapped_column(Enum('easy', 'medium', 'hard', name='difficulty_level'), server_default=text("'medium'::difficulty_level"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='assessments')
    coding_problems: Mapped[list['CodingProblems']] = relationship('CodingProblems', back_populates='assessment')


class Assignments(Base):
    __tablename__ = 'assignments'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='assignments_course_id_fkey'),
        PrimaryKeyConstraint('id', name='assignments_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    allowed_submission_types: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Enum('file', 'text', 'url', 'code', name='submission_type', _create_events=False)), server_default=text("'{text,file}'::submission_type[]"))
    points_possible: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('100'))
    rubric: Mapped[Optional[dict]] = mapped_column(JSONB)
    allow_late_submissions: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='assignments')
    assignment_submissions: Mapped[list['AssignmentSubmissions']] = relationship('AssignmentSubmissions', back_populates='assignment')


class Certificates(Base):
    __tablename__ = 'certificates'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='certificates_course_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='certificates_user_id_fkey'),
        PrimaryKeyConstraint('id', name='certificates_pkey'),
        UniqueConstraint('verification_code', name='certificates_verification_code_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    verification_code: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    issued_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    pdf_url: Mapped[Optional[str]] = mapped_column(Text)

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='certificates')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='certificates')


class ClassStreams(Base):
    __tablename__ = 'class_streams'
    __table_args__ = (
        CheckConstraint("type = ANY (ARRAY['announcement'::text, 'assignment_alert'::text, 'general'::text])", name='class_streams_type_check'),
        ForeignKeyConstraint(['author_id'], ['public.profiles.id'], ondelete='SET NULL', name='class_streams_author_id_fkey'),
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='class_streams_course_id_fkey'),
        PrimaryKeyConstraint('id', name='class_streams_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    attachment_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    type: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'general'::text"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    author: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='class_streams')
    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='class_streams')
    stream_comments: Mapped[list['StreamComments']] = relationship('StreamComments', back_populates='stream')


class Enrollments(Base):
    __tablename__ = 'enrollments'
    __table_args__ = (
        CheckConstraint('progress_percent >= 0 AND progress_percent <= 100', name='enrollments_progress_percent_check'),
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='enrollments_course_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='enrollments_user_id_fkey'),
        PrimaryKeyConstraint('id', name='enrollments_pkey'),
        UniqueConstraint('user_id', 'course_id', name='enrollments_user_id_course_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    enrolled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    progress_percent: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='enrollments')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='enrollments')
    lesson_progress: Mapped[list['LessonProgress']] = relationship('LessonProgress', back_populates='enrollment')


class Meetings(Base):
    __tablename__ = 'meetings'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='meetings_course_id_fkey'),
        PrimaryKeyConstraint('id', name='meetings_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    provider: Mapped[Optional[str]] = mapped_column(Enum('zoom', 'google_meet', 'internal', 'microsoft_teams', name='meeting_provider'), server_default=text("'internal'::meeting_provider"))
    meeting_link: Mapped[Optional[str]] = mapped_column(Text)
    recording_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='meetings')


class Modules(Base):
    __tablename__ = 'modules'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='modules_course_id_fkey'),
        PrimaryKeyConstraint('id', name='modules_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='modules')
    lessons: Mapped[list['Lessons']] = relationship('Lessons', back_populates='module')


class ProgramInvitations(Base):
    __tablename__ = 'program_invitations'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='program_invitations_course_id_fkey'),
        ForeignKeyConstraint(['institution_id'], ['public.institution_profiles.id'], ondelete='CASCADE', name='program_invitations_institution_id_fkey'),
        ForeignKeyConstraint(['trainee_id'], ['public.trainee_profiles.id'], ondelete='SET NULL', name='program_invitations_trainee_id_fkey'),
        PrimaryKeyConstraint('id', name='program_invitations_pkey'),
        UniqueConstraint('trainee_email', 'course_id', name='program_invitations_trainee_email_course_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    trainee_email: Mapped[str] = mapped_column(Text, nullable=False)
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    course_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    trainee_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    status: Mapped[Optional[str]] = mapped_column(Enum('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='invitation_status'), server_default=text("'PENDING'::invitation_status"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))

    course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='program_invitations')
    institution: Mapped[Optional['InstitutionProfiles']] = relationship('InstitutionProfiles', back_populates='program_invitations')
    trainee: Mapped[Optional['TraineeProfiles']] = relationship('TraineeProfiles', back_populates='program_invitations')


class AssignmentSubmissions(Base):
    __tablename__ = 'assignment_submissions'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['submitted'::text, 'graded'::text, 'returned'::text])", name='assignment_submissions_status_check'),
        ForeignKeyConstraint(['assignment_id'], ['public.assignments.id'], ondelete='CASCADE', name='assignment_submissions_assignment_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='assignment_submissions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='assignment_submissions_pkey'),
        UniqueConstraint('assignment_id', 'user_id', name='assignment_submissions_assignment_id_user_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    content_text: Mapped[Optional[str]] = mapped_column(Text)
    file_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))
    grade: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'submitted'::text"))

    assignment: Mapped[Optional['Assignments']] = relationship('Assignments', back_populates='assignment_submissions')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='assignment_submissions')


class CodingProblems(Base):
    __tablename__ = 'coding_problems'
    __table_args__ = (
        ForeignKeyConstraint(['assessment_id'], ['public.assessments.id'], ondelete='CASCADE', name='coding_problems_assessment_id_fkey'),
        PrimaryKeyConstraint('id', name='coding_problems_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    assessment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    starter_code: Mapped[Optional[dict]] = mapped_column(JSONB)
    supported_languages: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Enum('python', 'javascript', 'java', 'cpp', 'go', name='coding_language', _create_events=False)), server_default=text("'{javascript,python}'::coding_language[]"))
    order_index: Mapped[Optional[int]] = mapped_column(Integer)

    assessment: Mapped[Optional['Assessments']] = relationship('Assessments', back_populates='coding_problems')
    code_executions: Mapped[list['CodeExecutions']] = relationship('CodeExecutions', back_populates='problem')
    test_cases: Mapped[list['TestCases']] = relationship('TestCases', back_populates='problem')


class Lessons(Base):
    __tablename__ = 'lessons'
    __table_args__ = (
        ForeignKeyConstraint(['module_id'], ['public.modules.id'], ondelete='CASCADE', name='lessons_module_id_fkey'),
        PrimaryKeyConstraint('id', name='lessons_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Enum('text', 'video', 'pdf', 'quiz', 'assignment', name='content_type'), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    content_body: Mapped[Optional[str]] = mapped_column(Text)
    resource_url: Mapped[Optional[str]] = mapped_column(Text)
    is_preview_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    module: Mapped[Optional['Modules']] = relationship('Modules', back_populates='lessons')
    lesson_progress: Mapped[list['LessonProgress']] = relationship('LessonProgress', back_populates='lesson')


class StreamComments(Base):
    __tablename__ = 'stream_comments'
    __table_args__ = (
        ForeignKeyConstraint(['stream_id'], ['public.class_streams.id'], ondelete='CASCADE', name='stream_comments_stream_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='stream_comments_user_id_fkey'),
        PrimaryKeyConstraint('id', name='stream_comments_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    stream_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    stream: Mapped[Optional['ClassStreams']] = relationship('ClassStreams', back_populates='stream_comments')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='stream_comments')


class CodeExecutions(Base):
    __tablename__ = 'code_executions'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['passed'::text, 'failed'::text, 'runtime_error'::text, 'pending'::text])", name='code_executions_status_check'),
        ForeignKeyConstraint(['problem_id'], ['public.coding_problems.id'], ondelete='CASCADE', name='code_executions_problem_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.profiles.id'], ondelete='CASCADE', name='code_executions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='code_executions_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    code_submitted: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(Enum('python', 'javascript', 'java', 'cpp', 'go', name='coding_language'), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    problem_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    passed_cases: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    total_cases: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    status: Mapped[Optional[str]] = mapped_column(Text)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    problem: Mapped[Optional['CodingProblems']] = relationship('CodingProblems', back_populates='code_executions')
    user: Mapped[Optional['Profiles']] = relationship('Profiles', back_populates='code_executions')


class LessonProgress(Base):
    __tablename__ = 'lesson_progress'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['started'::text, 'completed'::text])", name='lesson_progress_status_check'),
        ForeignKeyConstraint(['enrollment_id'], ['public.enrollments.id'], ondelete='CASCADE', name='lesson_progress_enrollment_id_fkey'),
        ForeignKeyConstraint(['lesson_id'], ['public.lessons.id'], ondelete='CASCADE', name='lesson_progress_lesson_id_fkey'),
        PrimaryKeyConstraint('id', name='lesson_progress_pkey'),
        UniqueConstraint('enrollment_id', 'lesson_id', name='lesson_progress_enrollment_id_lesson_id_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    enrollment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    status: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'started'::text"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    last_position: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text("timezone('utc'::text, now())"))

    enrollment: Mapped[Optional['Enrollments']] = relationship('Enrollments', back_populates='lesson_progress')
    lesson: Mapped[Optional['Lessons']] = relationship('Lessons', back_populates='lesson_progress')


class TestCases(Base):
    __tablename__ = 'test_cases'
    __table_args__ = (
        ForeignKeyConstraint(['problem_id'], ['public.coding_problems.id'], ondelete='CASCADE', name='test_cases_problem_id_fkey'),
        PrimaryKeyConstraint('id', name='test_cases_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    problem_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    is_hidden: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    problem: Mapped[Optional['CodingProblems']] = relationship('CodingProblems', back_populates='test_cases')
