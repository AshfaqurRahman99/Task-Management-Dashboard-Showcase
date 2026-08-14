import streamlit as st
import json
import gspread
import pandas as pd
from datetime import date, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_cookies_controller import CookieController
import time
import html
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import timedelta


# --- ১.  পেজ কনফিগারেশন ---
st.set_page_config(
    page_title="PYF Task Management System", 
    page_icon="logo.png",  # লোগো বা ছবির ফাইলের নাম
    layout="wide", 
    initial_sidebar_state="collapsed"
)
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            
            /* ওপরের অতিরিক্ত স্পেস বা প্যাডিং কমানোর জন্য */
            .block-container {
                padding-top: 3.5rem !important;
            }
            
            /* Streamlit Cloud-এর প্রোফাইল ব্যাজ হাইড করার CSS */
            .viewerBadge_container__1QSob { display: none !important; }
            .viewerBadge_link__1S137 { display: none !important; }
            [data-testid="viewerBadge"] { display: none !important; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- ১.৫ ট্রান্সলেশন ডিকশনারি ---
translations = {
    "bn": {
        "update_header": "📝 আপনার নিজের টাস্কের স্ট্যাটাস আপডেট করুন",
        "select_task": "কোন টাস্কটি আপডেট করবেন? (Task ID)",
        "progress_status": "বর্তমান অবস্থা (Progress Status)",
        "final_report": "ফাইনাল রিপোর্ট লিংক",
        "comments": "আপনার মন্তব্য (Comments)",
        "submit_btn": "আপডেট সাবমিট করুন",
        "success_msg": "✅ টাস্ক সফলভাবে আপডেট হয়েছে!",
        
        "no_active_tasks": "এই ক্যাটাগরিতে বর্তমানে কোনো অ্যাকটিভ টাস্ক নেই।",
        "link": "লিংক",
        "report": "রিপোর্ট",
        "system_title": "🔐 টাস্ক ম্যানেজমেন্ট সিস্টেম",
        "login_error_msg": "❌ ইউজারনেম বা পাসওয়ার্ড ভুল হয়েছে!",
        "username_label": "Username (ইউজারনেম)",
        "password_label": "Password (পাসওয়ার্ড)",
        "login_btn": "Login (লগইন)",
        "verifying_account": "অ্যাকাউন্ট যাচাই করা হচ্ছে... <span style='font-size:65px;'>&#9995;</span> ",

        "loading_dashboard": "Please wait... <span style='font-size:75px;'>&#128515;</span> ",
        "toast_update_success": "✅ সফলভাবে আপডেট হয়েছে!",
        "role_label": "রোল: ",
        "profile_settings": "⚙️ প্রোফাইল সেটিংস",
        "new_fullname": "নতুন Full Name",
        "new_password": "নতুন পাসওয়ার্ড",
        "update_btn": "আপডেট করুন",
        "logout_btn": "🚪 লগআউট",
        "all_active_tasks": "📊 All active tasks (ওভারঅল প্রোগ্রেস)",
        "my_tasks": "📋 আমার নিজের টাস্কসমূহ",
        "team_tasks": "👥 আমার টিমের টাস্কসমূহ",
        "my_tasks_basic": "📋 আমার টাস্কসমূহ",
        "task_review_header": "👀 টাস্ক রিভিউ ও অ্যাপ্রুভাল (আপনার দেওয়া কাজগুলো রিভিউ করুন)",
        "select_default": "-- সিলেক্ট করুন --",
        "review_task_id": "কোন টাস্কটি রিভিউ করবেন? (Task ID)",
        "approval_action": "অ্যাপ্রুভাল অ্যাকশন:",
        "review_comment": "আপনার রিভিউ মন্তব্য দিন (যদি থাকে)",
        "review_note": "*(বিঃদ্রঃ 'OK' দিলে টাস্কটি ড্যাশবোর্ড থেকে ভ্যানিশ হয়ে যাবে)*",
        "review_submit_btn": "রিভিউ সাবমিট করুন",
        "review_error_msg": "⚠️ দয়া করে রিভিউ করার জন্য একটি সঠিক টাস্ক আইডি সিলেক্ট করুন!",
        
        "new_task_header": "➕ নতুন টাস্ক অ্যাসাইন করুন",
        "assignee_label": "যাকে টাস্ক দিবেন (Assignee)",
        "project_label": "প্রজেক্টের নাম (Project)",
        "task_name_label": "টাস্কের নাম (Task Name)",
        "docs_link_label": "প্রয়োজনীয় ডকুমেন্টস লিংক (Link)",
        "deadline_label": "ডেডলাইন (Deadline)",
        "submit_task_btn": "টাস্ক সাবমিট করুন",
        "task_name_error": "⚠️ টাস্কের নাম দেওয়া আবশ্যক!",
        "task_success_msg": "✅ সাকসেস! টাস্ক আইডি:",
        
        "modify_task_header": "✏️ আপনার অ্যাসাইন করা টাস্ক মডিফাই বা ক্যান্সেল করুন",
        "select_modify_task": "কোন টাস্কটি মডিফাই বা ক্যান্সেল করবেন? (Task ID)",
        "current_task_label": "বর্তমান টাস্ক:",
        "assigned_to_label": "যাকে দেওয়া হয়েছে:",
        "update_task_name_label": "টাস্কের নাম আপডেট করুন",
        "update_docs_link_label": "ডকুমেন্টস লিংক আপডেট করুন",
        "new_deadline_label": "নতুন ডেডলাইন",
        "select_action_label": "অ্যাকশন সিলেক্ট করুন:",
        "action_update": "আপডেট করুন (Update)",
        "action_cancel": "টাস্ক ডিলিট/ক্যান্সেল করুন (Cancel)",
        "submit_generic_btn": "সাবমিট করুন",
        "task_cancel_success": "✅ টাস্কটি সফলভাবে ক্যান্সেল করা হয়েছে এবং ইউজারের কাছে ইমেইল পাঠানো হয়েছে!",
        "task_update_success": "✅ টাস্কটি সফলভাবে আপডেট করা হয়েছে এবং ইউজারের কাছে ইমেইল পাঠানো হয়েছে!",
        "email_task_name": "- টাস্কের নাম: ",
        "email_deadline": "\n- ডেডলাইন: ",
        "email_link": "\n- লিংক: "
    },
    "en": {
        "update_header": "📝 Update Your Task Status",
        "select_task": "Which task to update? (Task ID)",
        "progress_status": "Current Status (Progress)",
        "final_report": "Final Report Link",
        "comments": "Your Comments (Optional)",
        "submit_btn": "Submit Update",
        "success_msg": "✅ Task updated successfully!",
        
        "no_active_tasks": "No active tasks currently in this category.",
        "link": "Link",
        "report": "Report",
        "system_title": "🔐 Task Management System",
        "login_error_msg": "❌ Invalid Username or Password!",
        "username_label": "Username",
        "password_label": "Password",
        "login_btn": "Login",
        "verifying_account": "Verifying account... <span style='font-size:65px;'>&#9995;</span> ",

        "loading_dashboard": "Loading dashboard... <span style='font-size:75px;'>&#128515;</span> ",
        "toast_update_success": "✅ Successfully updated!",
        "role_label": "Role: ",
        "profile_settings": "⚙️ Profile Settings",
        "new_fullname": "New Full Name",
        "new_password": "New Password",
        "update_btn": "Update",
        "logout_btn": "🚪 Logout",
        "all_active_tasks": "📊 All Active Tasks (Overall Progress)",
        "my_tasks": "📋 My Tasks",
        "team_tasks": "👥 My Team's Tasks",
        "my_tasks_basic": "📋 My Tasks",
        "task_review_header": "👀 Task Review & Approval",
        "select_default": "-- Select --",
        "review_task_id": "Which task to review? (Task ID)",
        "approval_action": "Approval Action:",
        "review_comment": "Provide your review comment (if any)",
        "review_note": "*(Note: Selecting 'OK' will remove the task from the dashboard)*",
        "review_submit_btn": "Submit Review",
        "review_error_msg": "⚠️ Please select a valid task ID for review!",
        
        "new_task_header": "➕ Assign New Task",
        "assignee_label": "Assignee",
        "project_label": "Project Name",
        "task_name_label": "Task Name",
        "docs_link_label": "Necessary Documents (Link)",
        "deadline_label": "Deadline",
        "submit_task_btn": "Submit Task",
        "task_name_error": "⚠️ Task name is required!",
        "task_success_msg": "✅ Success! Task ID:",
        
        "modify_task_header": "✏️ Modify or Cancel Assigned Tasks",
        "select_modify_task": "Which task to modify/cancel? (Task ID)",
        "current_task_label": "Current Task:",
        "assigned_to_label": "Assigned To:",
        "update_task_name_label": "Update Task Name",
        "update_docs_link_label": "Update Documents Link",
        "new_deadline_label": "New Deadline",
        "select_action_label": "Select Action:",
        "action_update": "Update Task",
        "action_cancel": "Cancel/Delete Task",
        "submit_generic_btn": "Submit",
        "task_cancel_success": "✅ Task successfully cancelled and email sent to user!",
        "task_update_success": "✅ Task successfully updated and email sent to user!",
        "email_task_name": "- Task Name: ",
        "email_deadline": "\n- Deadline: ",
        "email_link": "\n- Link: "
    }
}


# --- ২. ল্যাঙ্গুয়েজ সিলেকশন ও মেমোরি সেটআপ ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'bn'

# শর্টকাট ফাংশন
def t(key):
    return translations[st.session_state['lang']].get(key, key)


# --- 🍪 কুকি কন্ট্রোলার ইনিশিয়ালাইজ ---
cookie_controller = CookieController()

# (এর পরের গুগল শিট কানেকশন, ইমেইল ফাংশন এবং অন্যান্য কোডগুলো আগের মতোই থাকবে, সেখানে কোনো পরিবর্তন নেই!)

# --- গুগল শিট কানেকশন ---
creds_json = st.secrets["google_credentials"]
creds_dict = json.loads(creds_json)
gc = gspread.service_account_from_dict(creds_dict)
SHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE"  # এখানে আপনার গুগল শিটের URL বসান
sh = gc.open_by_url(SHEET_URL)
tasks_sheet = sh.worksheet("Tasks")
users_sheet = sh.worksheet("Users")
projects_sheet = sh.worksheet("Projects") 

# ==========================================
# ইমেইল পাঠানোর ফাংশনসমূহ (SMTP Automation)
# ==========================================

# --- ১. নতুন টাস্ক অ্যাসাইনমেন্ট এর ইমেইল ---
def send_task_notification(receiver_email, task_id, task_name, project_name, assigned_by, deadline):
    try:
        sender_email = st.secrets["email_settings"]["sender_email"]
        app_password = st.secrets["email_settings"]["app_password"]
        smtp_server = st.secrets["email_settings"].get("smtp_server", "smtp.gmail.com")
        smtp_port = int(st.secrets["email_settings"].get("smtp_port", 587))
    except KeyError:
        return False 
        
    if app_password == "replace_this_with_real_password_later" or not receiver_email:
        return False

    # ডেডলাইন ফরম্যাট পরিবর্তন (YYYY-MM-DD থেকে DD Month Name, YYYY)
    try:
        deadline_dt = datetime.strptime(str(deadline), "%Y-%m-%d")
        formatted_deadline = deadline_dt.strftime("%d %B, %Y")
    except Exception:
        formatted_deadline = deadline

    subject = f"New Task Assigned: {task_id} | PATH Youth Forum"
    
    # Bilingual Email Body (English + Bengali)
    body = f"""Hello / হ্যালো,

A new task has been assigned to you. / আপনাকে একটি নতুন টাস্ক অ্যাসাইন করা হয়েছে।

📌 Task ID / টাস্ক আইডি: {task_id}
📁 Project / প্রজেক্ট: {project_name}
📝 Task Name / টাস্কের নাম: {task_name}
👤 Assigned By / অ্যাসাইন করেছেন: {assigned_by}
⏰ Deadline / ডেডলাইন: {formatted_deadline} (11.59 PM)

Please log in to the Task Management System to view details and start working.
বিস্তারিত দেখতে এবং কাজ শুরু করতে সিস্টেমে লগইন করুন:
🔗 Task Manager Link: https://pyf-task-manager.streamlit.app/

Thank You / ধন্যবাদ,
PYF Task Admin
PATH Youth Forum
"""
    
    msg = MIMEMultipart()
    msg['From'] = f"PYF Task Admin <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


# --- ২. টাস্ক আপডেট বা ক্যান্সেল এর ইমেইল ---
def send_task_update_email(receiver_email, task_id, task_name, update_type, extra_info=""):
    try:
        sender_email = st.secrets["email_settings"]["sender_email"]
        app_password = st.secrets["email_settings"]["app_password"]
        smtp_server = st.secrets["email_settings"].get("smtp_server", "smtp.gmail.com")
        smtp_port = int(st.secrets["email_settings"].get("smtp_port", 587))
    except KeyError:
        return False 
        
    if app_password == "replace_this_with_real_password_later" or not receiver_email:
        return False

    if update_type == "Cancelled":
        subject = f"Task Cancelled: {task_id} | PATH Youth Forum"
        body = f"""Hello / হ্যালো,

A task assigned to you has been Cancelled. / আপনাকে অ্যাসাইন করা একটি টাস্ক বাতিল করা হয়েছে।

📌 Task ID / টাস্ক আইডি: {task_id}
📝 Task Name / টাস্কের নাম: {task_name}

You no longer need to work on this task. / আপনাকে এই টাস্কটি নিয়ে আর কাজ করতে হবে না।

Thank You / ধন্যবাদ,
PYF Task Admin
PATH Youth Forum
"""
    else:
        subject = f"Task Updated: {task_id} | PATH Youth Forum"
        body = f"""Hello / হ্যালো,

Changes have been made to a task assigned to you. / আপনাকে অ্যাসাইন করা একটি টাস্কে পরিবর্তন আনা হয়েছে।

📌 Task ID / টাস্ক আইডি: {task_id}

Updates / নতুন আপডেটসমূহ:
{extra_info}

Please log in to the system for more details. / বিস্তারিত জানতে সিস্টেমে লগইন করুন:
🔗 Task Manager Link: https://pyf-task-manager.streamlit.app/

Thank You / ধন্যবাদ,
PYF Task Admin
PATH Youth Forum
"""
    
    msg = MIMEMultipart()
    msg['From'] = f"PYF Task Admin <{sender_email}>"  # Updated to match the first function
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Update Email failed: {e}")
        return False

# --- সেশন স্টেট ইনিশিয়ালাইজেশন ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'full_name' not in st.session_state:
    st.session_state['full_name'] = ""
if 'role' not in st.session_state:
    st.session_state['role'] = ""
if 'login_error' not in st.session_state:
    st.session_state['login_error'] = False

def get_users_data():
    return pd.DataFrame(users_sheet.get_all_records())

# --- 🍪 সিকিউর কুকি চেক (JWT অটো-লগইন লজিক) ---
stored_token = cookie_controller.get('pyf_session')
if stored_token and not st.session_state['logged_in']:
    try:
        # টোকেন ভেরিফাই ও ডিকোড করা
        decoded_payload = jwt.decode(stored_token, st.secrets.get("cookie_secret", "fallback_secret"), algorithms=["HS256"])
        valid_username = decoded_payload.get('user')
        
        users_df = get_users_data()
        user_row = users_df[users_df['Username'] == valid_username]
        
        if not user_row.empty:
            st.session_state['logged_in'] = True
            st.session_state['username'] = valid_username
            st.session_state['role'] = user_row.iloc[0]['Role']
            st.session_state['full_name'] = user_row.iloc[0].get('Full Name', valid_username)
            st.rerun()
    except jwt.ExpiredSignatureError:
        # কুকির মেয়াদ শেষ হয়ে গেলে লগআউট করে দেবে
        cookie_controller.remove('pyf_session')
    except jwt.InvalidTokenError:
        # কেউ কুকি ম্যানুয়ালি চেঞ্জ করলে টোকেন ইনভ্যালিড হয়ে যাবে
        pass

# --- 🌀 প্রফেশনাল ডটস লোডার ---
def get_dots_loader_html(message="যাচাই করা হচ্ছে..."):
    return f"""
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 70vh;">
        <div style="display: flex; gap: 12px;">
            <div style="width: 16px; height: 16px; background-color: #00cc96; border-radius: 50%; animation: bounce 0.6s infinite alternate; animation-delay: 0s;"></div>
            <div style="width: 16px; height: 16px; background-color: #00cc96; border-radius: 50%; animation: bounce 0.6s infinite alternate; animation-delay: 0.2s;"></div>
            <div style="width: 16px; height: 16px; background-color: #00cc96; border-radius: 50%; animation: bounce 0.6s infinite alternate; animation-delay: 0.4s;"></div>
        </div>
        <h4 style="color: #00cc96; margin-top: 25px; font-family: sans-serif; letter-spacing: 1px;">{message}</h4>
    </div>
    <style>
        @keyframes bounce {{
            from {{ transform: translateY(0); opacity: 0.8; }}
            to {{ transform: translateY(-20px); opacity: 1; }}
        }}
    </style>
    """

def get_tasks_data():
    try:
        rows = tasks_sheet.get_all_values()
        if not rows or len(rows) <= 1:
            return pd.DataFrame(columns=[
                'Task ID', 'Assignee', 'Project Name', 'Assigned By', 
                'Task Name', 'Necessary Documents', 'Task Initiation', 
                'Deadline', 'Progress Status', 'Final Report', 'Comments', 'Approval Status', 'Completion Time'
            ])
        header = [str(col).strip() for col in rows[0]]
        df = pd.DataFrame(rows[1:], columns=header)
        
        if 'Approval Status' not in df.columns:
            df['Approval Status'] = "Pending"
        if 'Completion Time' not in df.columns:
            df['Completion Time'] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=[
            'Task ID', 'Assignee', 'Project Name', 'Assigned By', 
            'Task Name', 'Necessary Documents', 'Task Initiation', 
            'Deadline', 'Progress Status', 'Final Report', 'Comments', 'Approval Status', 'Completion Time'
        ])

def get_project_list():
    data = projects_sheet.get_all_records()
    if not data: return ["No Projects Found"]
    df = pd.DataFrame(data)
    return df['Project Name'].dropna().unique().tolist()

# --- 📊 প্রোগ্রেস ও টাইম ডিলে হিসাব করার ফাংশন ---
def get_progress_html(row):
    status = row.get('Progress Status', 'To-Do')
    if status == "To-Do": 
        pct, color = 0, "#ff4b4b"
    elif status == "In Progress": 
        pct, color = 50, "#faca2b"
    elif status == "Review": 
        pct, color = 75, "#17a2b8"
    elif status == "Completed":
        pct = 100
        color = "#00cc96"
        extra_text = ""
        try:
            deadline_str = row.get('Deadline', '')
            completion_str = row.get('Completion Time', '')
            
            deadline_dt = pd.to_datetime(deadline_str, errors='coerce')
            if pd.notna(deadline_dt):
                if deadline_dt.hour == 0 and deadline_dt.minute == 0 and deadline_dt.second == 0:
                    deadline_dt = deadline_dt.replace(hour=23, minute=59, second=59)
                
                if pd.notna(completion_str) and str(completion_str).strip() != "":
                    completion_dt = pd.to_datetime(completion_str, errors='coerce')
                else:
                    completion_dt = pd.Timestamp.now()
                    
                if pd.notna(completion_dt):
                    if completion_dt <= deadline_dt:
                        extra_text = " <span style='color: #00cc96; font-size: 11px;'>(In time)</span>"
                    else:
                        diff_hours = (completion_dt - deadline_dt).total_seconds() / 3600.0
                        extra_text = f" <span style='color: #ff4b4b; font-size: 11px;'>(Delay: {diff_hours:.1f} hour)</span>"
        except Exception:
            pass
        
        return f"<div style='min-width: 90px;'><span style='font-weight: 500;'>{status}</span> <span style='font-size: 11px; color: gray;'>({pct}%)</span>{extra_text}<div style='margin-top: 4px; width: 100%; background-color: rgba(128,128,128,0.25); border-radius: 4px; height: 6px;'><div style='width: {pct}%; background-color: {color}; height: 6px; border-radius: 4px;'></div></div></div>"
    else:
        pct, color = 0, "#888"

    return f"<div style='min-width: 90px;'><span style='font-weight: 500;'>{status}</span> <span style='font-size: 11px; color: gray;'>({pct}%)</span><div style='margin-top: 4px; width: 100%; background-color: rgba(128,128,128,0.25); border-radius: 4px; height: 6px;'><div style='width: {pct}%; background-color: {color}; height: 6px; border-radius: 4px;'></div></div></div>"

# --- 📊 কাস্টম টেবিল রেন্ডারিং ফাংশন ---
def render_task_table(df, title):
    st.markdown(f"### {title}")
    if df.empty:
        st.info(t("no_active_tasks")) # ডায়নামিক টেক্সট
        return
        
    view_df = df.copy()

    try:
        if 'Deadline' in view_df.columns:
            view_df['Deadline'] = pd.to_datetime(view_df['Deadline'], errors='coerce').dt.strftime('%d, %b %Y').fillna("")
        if 'Initiation' in view_df.columns:
            view_df['Initiation'] = pd.to_datetime(view_df['Initiation'], errors='coerce').dt.strftime('%d, %b %Y').fillna("")
    except:
        pass 
    
    # 🔴 XSS প্রিভেনশন: কাস্টম HTML বানানোর আগে সব স্ট্রিং ডেটাকে এস্কেপ (Escape) করে দেওয়া হচ্ছে
    for col in view_df.columns:
        if view_df[col].dtype == 'object':
            view_df[col] = view_df[col].apply(lambda x: html.escape(str(x)) if pd.notnull(x) else x)

    def make_link(url, text):
        if pd.isna(url) or str(url).strip() == "": return ""
        url_str = str(url).strip()
        
        # URL ভ্যালিডেশন (Malicious লিংক ইনজেকশন ঠেকানোর জন্য)
        if not url_str.startswith(('http://', 'https://')):
            return html.escape(url_str) # লিংক না হলে শুধু সেফ টেক্সট হিসেবে দেখাবে
            
        return f"<a href='{html.escape(url_str)}' target='_blank'>🔗 {html.escape(text)}</a>"
        
    if 'Necessary Documents' in view_df.columns:
        # 'link' টেক্সটকেও এস্কেপ করা হলো সেফটির জন্য
        view_df['Necessary Documents'] = view_df['Necessary Documents'].apply(lambda x: make_link(x, html.escape(t("link")))) 
    if 'Final Report' in view_df.columns:
        view_df['Final Report'] = view_df['Final Report'].apply(lambda x: make_link(x, html.escape(t("report"))))

    if 'Progress Status' in view_df.columns:
        view_df['Progress Status'] = view_df.apply(get_progress_html, axis=1)
        
    rename_map = {
        'Project Name': 'Project',
        'Necessary Documents': 'Docs',
        'Task Initiation': 'Initiation',
        'Progress Status': 'Progress',
        'Approval Status': 'Approval',
        'Final Report': 'Report'
    }
    view_df = view_df.rename(columns=rename_map)
    
    columns_sequence = [
        'Assignee', 'Project', 'Task ID', 'Assigned By', 
        'Task Name', 'Docs', 'Initiation', 
        'Deadline', 'Progress', 'Approval', 'Report', 'Comments'
    ]
    view_df = view_df[[c for c in columns_sequence if c in view_df.columns]]
    
    table_html = view_df.to_html(escape=False, index=False, classes="custom-wrap-table")
    
    custom_css = """
    <style>
        .custom-wrap-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; font-family: sans-serif; }
        .custom-wrap-table th, .custom-wrap-table td { border: 1px solid rgba(128, 128, 128, 0.3); padding: 10px; text-align: left; word-break: normal; overflow-wrap: break-word; white-space: normal !important; vertical-align: top; }
        .custom-wrap-table th { background-color: rgba(128, 128, 128, 0.15); font-weight: bold; }
        .custom-wrap-table a { color: #4da6ff; text-decoration: none; }
        .custom-wrap-table a:hover { text-decoration: underline; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(table_html, unsafe_allow_html=True)

# ==========================================
# 1. লগইন পেইজ 
# ==========================================
def login_page():
    login_placeholder = st.empty()
    
    with login_placeholder.container():
        # ডায়নামিক টেক্সট ও ভার্সন ব্যাজ একসাথে বসানো হয়েছে (জিরো গ্যাপ)
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <h1 style='color: #00cc96; margin-bottom: 0px; padding-bottom: 0px;'>PATH Youth Forum</h1>
                <h3 style='margin-top: 5px; margin-bottom: 10px;'>{t('system_title')}</h3>
                <span style='background-color: #f0f2f6; border: 1px solid #d1d5db; color: #4b5563; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;'>
                    V 1.2
                </span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.write("---")
        #     <div style="text-align: center; margin-top: 5px; margin-bottom: 15px;">
        #         <span style="background-color: #f0f2f6; border: 1px solid #d1d5db; color: #4b5563; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;">
        #             V 1.1
        #         </span>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )
        
        if st.session_state['login_error']:
            st.error(t("login_error_msg")) # ডায়নামিক টেক্সট
            st.session_state['login_error'] = False
            
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username_input = st.text_input(t("username_label")) # ডায়নামিক টেক্সট
                password_input = st.text_input(t("password_label"), type="password") # ডায়নামিক টেক্সট
                submit_login = st.form_submit_button(t("login_btn"), use_container_width=True) # ডায়নামিক টেক্সট
                
    if submit_login:
        login_placeholder.empty()
        
        loader_placeholder = st.empty()
        loader_placeholder.markdown(get_dots_loader_html(t("verifying_account")), unsafe_allow_html=True)
        
        users_df = get_users_data()
        
        # প্রথমে শুধু ইউজারনেম দিয়ে ডেটা খুঁজবে
        user = users_df[users_df['Username'] == username_input]
        
        loader_placeholder.empty()
        
        # পাসওয়ার্ড চেক (Werkzeug হ্যাশ ভেরিফিকেশন)
        if not user.empty and check_password_hash(str(user.iloc[0]['Password']), str(password_input)):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username_input
            st.session_state['role'] = user.iloc[0]['Role']
            st.session_state['full_name'] = user.iloc[0].get('Full Name', username_input)
            
            # ইনসিকিউর কুকির বদলে JWT এনক্রিপ্টেড টোকেন তৈরি করা হচ্ছে
            token_payload = {
                'user': username_input, 
                'exp': datetime.utcnow() + timedelta(days=7) # ৭ দিন পর কুকি এক্সপায়ার হবে
            }
            # st.secrets["cookie_secret"] এ একটি রেন্ডম স্ট্রিং (যেমন: "my_super_secret_key_123") সেভ করে রাখবেন
            secure_token = jwt.encode(token_payload, st.secrets.get("cookie_secret", "fallback_secret"), algorithm="HS256")
            
            cookie_controller.set('pyf_session', secure_token)
            
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.session_state['login_error'] = True
            st.rerun()


# ==========================================
# 2. মেইন ড্যাশবোর্ড
# ==========================================
def main_dashboard():
    dashboard_loader = st.empty()
    dashboard_loader.markdown(get_dots_loader_html(t("loading_dashboard")), unsafe_allow_html=True)

    users_df = get_users_data()
    tasks_df = get_tasks_data()
    
    dashboard_loader.empty()

    if st.session_state.get('update_success', False):
        st.toast(t("toast_update_success"), icon="✅")
        st.session_state['update_success'] = False

    # --- নেভিগেশন বার ---
    nav_col1, nav_col2, nav_col3 = st.columns([6, 2, 1])
    with nav_col1:
        st.markdown(f"## 👤 {st.session_state['full_name']} <br><span style='font-size: 16px; color: gray;'>{t('role_label')}{st.session_state['role']}</span>", unsafe_allow_html=True)
    with nav_col2:
        with st.popover(t("profile_settings"), use_container_width=True):
            
            # --- ল্যাঙ্গুয়েজ চেঞ্জ অপশন (ফর্মের বাইরে রাখা হয়েছে যাতে সাথে সাথে কাজ করে) ---
            current_lang_idx = 0 if st.session_state['lang'] == 'bn' else 1
            selected_lang = st.radio("🌐 Language / ভাষা", ["বাংলা", "English"], index=current_lang_idx, horizontal=True)
            
            # ভাষা পরিবর্তন হলে সাথে সাথে পেজ রিলোড হবে
            if (selected_lang == "English" and st.session_state['lang'] == 'bn') or \
               (selected_lang == "বাংলা" and st.session_state['lang'] == 'en'):
                st.session_state['lang'] = 'en' if selected_lang == "English" else 'bn'
                st.rerun()
            
            st.markdown("---")
            
            # --- প্রোফাইল আপডেট ফর্ম ---
            with st.form("profile_update_form"):
                new_fullname = st.text_input(t("new_fullname"), value=st.session_state['full_name'])
                new_password = st.text_input(t("new_password"), type="password")
                
                if st.form_submit_button(t("update_btn"), use_container_width=True):
                    # চেক করবে নাম পরিবর্তন হয়েছে কিনা অথবা নতুন পাসওয়ার্ড দেওয়া হয়েছে কিনা
                    name_changed = (new_fullname and new_fullname != st.session_state['full_name'])
                    password_given = bool(new_password)
                    
                    if name_changed or password_given:
                        row_index = users_df.index[users_df['Username'] == st.session_state['username']].tolist()[0] + 2
                        
                        if name_changed:
                            users_sheet.update_cell(row_index, users_df.columns.get_loc("Full Name") + 1, new_fullname)
                            st.session_state['full_name'] = new_fullname
                            
                        if password_given:
                            hashed_pw = generate_password_hash(new_password)
                            users_sheet.update_cell(row_index, users_df.columns.get_loc("Password") + 1, hashed_pw)
                            
                        st.session_state['update_success'] = True
                        st.rerun()
                        
    with nav_col3:
        if st.button(t("logout_btn"), use_container_width=True):
            st.session_state.clear()
            
            # নতুন সিকিউর সেশন কুকি রিমুভ করা
            if cookie_controller.get('pyf_session'):
                cookie_controller.remove('pyf_session')
                
            # যদি ব্রাউজারে আগে থেকে কোনো পুরোনো pyf_user কুকি সেভ করা থাকে, সেটাও ক্লিয়ার করে দেওয়া
            if cookie_controller.get('pyf_user'):
                cookie_controller.remove('pyf_user')
                
            import time
            time.sleep(1)
            st.rerun()
            
    st.markdown("---")

    active_tasks_df = tasks_df[~tasks_df['Approval Status'].isin(['OK', 'Cancelled'])]

    # --- ১. ড্যাশবোর্ড ভিউ ---
    my_tasks = active_tasks_df[active_tasks_df['Assignee'] == st.session_state['username']]
    assigned_by_me = active_tasks_df[active_tasks_df['Assigned By'] == st.session_state['username']]
    
    if st.session_state['role'] == "Top Management":
        render_task_table(active_tasks_df, t("all_active_tasks"))
    elif st.session_state['role'] == "Mid Management":
        render_task_table(my_tasks, t("my_tasks"))
        st.write("")
        render_task_table(assigned_by_me, t("team_tasks"))
    else:
        render_task_table(my_tasks, t("my_tasks_basic"))

    st.markdown("---")

    # --- ২. টাস্ক রিভিউ ও অ্যাপ্রুভাল ---
    if st.session_state['role'] in ["Top Management", "Mid Management"]:
        tasks_to_review = assigned_by_me[assigned_by_me['Progress Status'].isin(['Completed', 'Review'])]
        
        if not tasks_to_review.empty:
            with st.expander(t("task_review_header"), expanded=True):
                with st.form("review_task_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        task_options = [t("select_default")] + tasks_to_review['Task ID'].tolist()
                        review_task_id = st.selectbox(t("review_task_id"), options=task_options)
                        review_action = st.radio(t("approval_action"), options=["OK", "Hold"], horizontal=True)
                    with col2:
                        review_comment = st.text_input(t("review_comment"))
                        st.write(t("review_note"))
                        
                    if st.form_submit_button(t("review_submit_btn"), use_container_width=True):
                        if review_task_id == t("select_default"):
                            st.error(t("review_error_msg"))
                        else:
                            row_idx = tasks_df.index[tasks_df['Task ID'] == review_task_id].tolist()[0] + 2
                            tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Approval Status") + 1, review_action)
                            if review_comment:
                                tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Comments") + 1, review_comment)
                            st.session_state['update_success'] = True
                            st.rerun()

    # --- ৩. টাস্ক স্ট্যাটাস আপডেট সিস্টেম ---
    if not my_tasks.empty:
        with st.expander(t("update_header"), expanded=False):
            with st.form("update_status_form"):
                col1, col2 = st.columns(2)
                with col1:
                    selected_task = st.selectbox(t("select_task"), options=my_tasks['Task ID'].tolist())
                    new_status = st.selectbox(t("progress_status"), options=["To-Do", "In Progress", "Review", "Completed"])
                with col2:
                    final_report = st.text_input(t("final_report"))
                    comments = st.text_input(t("comments"))
                
                if st.form_submit_button(t("submit_btn")):
                    from datetime import datetime 
                    
                    row_idx = tasks_df.index[tasks_df['Task ID'] == selected_task].tolist()[0] + 2
                    
                    # ১. স্ট্যাটাস আপডেট
                    tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Progress Status") + 1, new_status)
                    
                    # ২. Submission Time আপডেট 
                    if 'Submission Time' in tasks_df.columns:
                        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Submission Time") + 1, timestamp_str)
                    
                    # ৩. অন্যান্য তথ্য আপডেট
                    if final_report: 
                        tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Final Report") + 1, final_report)
                    if comments: 
                        tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Comments") + 1, comments)
                        
                    st.session_state['update_success'] = True
                    st.rerun()

    # --- ৪. নতুন টাস্ক অ্যাসাইনমেন্ট ---
    if st.session_state['role'] in ["Top Management", "Mid Management"]:
        st.markdown("---")
        st.subheader(t("new_task_header"))
        
        current_user = st.session_state['username']
        
        if st.session_state['role'] == "Top Management":
            assignee_options = users_df[users_df['Username'] != current_user]['Username'].tolist()
        else:
            assignee_options = users_df[(users_df['Role'] != 'Top Management') & (users_df['Username'] != current_user)]['Username'].tolist()
            
        project_options = get_project_list()
        
        with st.form("new_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                assignee = st.selectbox(t("assignee_label"), options=assignee_options)
                project_name = st.selectbox(t("project_label"), options=project_options)
                task_name = st.text_input(t("task_name_label"))
            with col2:
                docs = st.text_input(t("docs_link_label"))
                deadline = st.date_input(t("deadline_label"))
                
            if st.form_submit_button(t("submit_task_btn"), use_container_width=True):
                if not task_name:
                    st.error(t("task_name_error"))
                else:
                    if not tasks_df.empty:
                        try:
                            last_id = tasks_df.iloc[-1]['Task ID']
                            id_num = int(last_id.split('-')[1]) + 1
                            new_task_id = f"T-{id_num:03d}"
                        except:
                            new_task_id = f"T-{len(tasks_df)+1:03d}"
                    else:
                        new_task_id = "T-001"
                    
                    new_row = [
                        new_task_id, assignee, project_name, st.session_state['username'], 
                        task_name, docs, str(date.today()), str(deadline), "To-Do", "", "", "Pending", ""
                    ]
                    tasks_sheet.append_row(new_row)
                    
                    try:
                        assignee_email = None
                        if 'Email' in users_df.columns:
                            assignee_row = users_df[users_df['Username'] == assignee]
                            if not assignee_row.empty:
                                assignee_email = str(assignee_row.iloc[0]['Email'])
                        
                        if assignee_email:
                            send_task_notification(assignee_email, new_task_id, task_name, project_name, st.session_state['full_name'], str(deadline))
                    except Exception as e:
                        print(f"Error handling email: {e}")
                    
                    # ডায়নামিক সাকসেস মেসেজ
                    st.success(f"{t('task_success_msg')} **{new_task_id}**")
                    st.rerun()
                    
        # --- ৫. টাস্ক মডিফিকেশন বা ক্যান্সেল ---
    if not assigned_by_me.empty:
        st.markdown("---")
        with st.expander(t("modify_task_header"), expanded=False):
            edit_task_id = st.selectbox(t("select_modify_task"), options=[t("select_default")] + assigned_by_me['Task ID'].tolist(), key="edit_task_select")
            
            if edit_task_id != t("select_default"):
                task_row = tasks_df[tasks_df['Task ID'] == edit_task_id].iloc[0]
                
                with st.form("edit_task_form"):
                    st.markdown(f"**{t('current_task_label')}** {task_row['Task Name']} | **{t('assigned_to_label')}** {task_row['Assignee']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        edit_t_name = st.text_input(t("update_task_name_label"), value=task_row['Task Name'])
                        edit_t_docs = st.text_input(t("update_docs_link_label"), value=str(task_row['Necessary Documents']))
                    with c2:
                        try:
                            curr_dl = datetime.strptime(str(task_row['Deadline']), "%Y-%m-%d").date()
                        except:
                            curr_dl = date.today()
                        edit_t_deadline = st.date_input(t("new_deadline_label"), value=curr_dl)
                        edit_action = st.radio(t("select_action_label"), options=[t("action_update"), t("action_cancel")])
                        
                    if st.form_submit_button(t("submit_generic_btn"), use_container_width=True):
                        row_idx = tasks_df.index[tasks_df['Task ID'] == edit_task_id].tolist()[0] + 2
                        
                        # ইউজারের ইমেইল বের করার লজিক
                        assignee_email = None
                        if 'Email' in users_df.columns:
                            assignee_row = users_df[users_df['Username'] == task_row['Assignee']]
                            if not assignee_row.empty:
                                assignee_email = str(assignee_row.iloc[0]['Email'])

                        if edit_action == t("action_cancel"):
                            # সফট ডিলিট: শুধু স্ট্যাটাস পরিবর্তন হবে
                            tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Approval Status") + 1, "Cancelled")
                            if assignee_email:
                                send_task_update_email(assignee_email, edit_task_id, task_row['Task Name'], "Cancelled")
                            st.success(t("task_cancel_success"))
                        else:
                            # আপডেট লজিক
                            tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Task Name") + 1, edit_t_name)
                            tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Necessary Documents") + 1, edit_t_docs)
                            tasks_sheet.update_cell(row_idx, tasks_df.columns.get_loc("Deadline") + 1, str(edit_t_deadline))
                            
                            if assignee_email:
                                extra_info = f"{t('email_task_name')}{edit_t_name}{t('email_deadline')}{edit_t_deadline.strftime('%d %B, %Y')}{t('email_link')}{edit_t_docs}"
                                send_task_update_email(assignee_email, edit_task_id, edit_t_name, "Updated", extra_info)
                            
                            st.success(t("task_update_success"))
                        
                        st.session_state['update_success'] = True
                        st.rerun()


# ==========================================
# 3. রাউটিং লজিক
# ==========================================
if not st.session_state['logged_in']:
    login_page()
else:
    main_dashboard()
