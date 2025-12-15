from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, Response, flash
from functools import wraps
import sqlite3
import io
import json
from collections import Counter
import re
from datetime import datetime
import os
import csv
from io import StringIO
from urllib.parse import unquote, quote

app = Flask(__name__)
app.secret_key = 'batir-admin-secret-key-2024'

# Конфигурация логина
ADMIN_CREDENTIALS = {
    'login': 'Batir',
    'password': 'admin123'
}

# Переводы для админ-панели
TRANSLATIONS = {
    'uz': {
        'dashboard': 'Dashboard',
        'users': 'Foydalanuvchilar',
        'analytics': 'Analitika',
        'settings': 'Sozlamalar',
        'export_data': 'Ma\'lumotlarni yuklash',
        'logout': 'Chiqish',
        'total_users': 'Jami foydalanuvchilar',
        'completed_surveys': 'Yakunlangan so\'rovnomalar',
        'completion_rate': 'Yakunlanish darajasi',
        'users_who_started': 'So\'rovnomani boshlaganlar',
        'bank_statistics': 'Banklar statistikasi',
        'yes': 'Ha',
        'no': 'Yo\'q',
        'partially': 'Qisman',
        'details': 'Batafsil',
        'information': 'Ma\'lumot',
        'delete': 'O\'chirish',
        'back': 'Orqaga',
        'save': 'Saqlash',
        'change_password': 'Parolni o\'zgartish',
        'old_password': 'Eski parol',
        'new_password': 'Yangi parol',
        'confirm_password': 'Yangi parolni tasdiqlang',
        'password_changed': 'Parol muvaffaqiyatli o\'zgartirildi',
        'password_error': 'Parol noto\'g\'ri',
        'language': 'Til',
        'percentage': 'Foiz',
        'count': 'Soni',
        'total': 'Jami',
        'export_excel': 'Excel-ga yuklash',
        'people': 'kishi',
        'other_bank': 'Boshqa bank',
        'bank_users': 'Bank foydalanuvchilari',
        'view_details': 'Batafsil',
        'total_users_in_bank': 'Bankdagi jami foydalanuvchilar',
        'completed_surveys_in_bank': 'Bankda yakunlangan so\'rovnomalar',
        'completion_rate_in_bank': 'Bankda yakunlanish darajasi',
        'export_to_excel': 'Excel-ga yuklash',
        'back_to_dashboard': 'Dashboardga qaytish',
        'bank_name': 'Bank nomi',
        'user_count': 'Foydalanuvchilar soni',
        'survey_responses': 'So\'rovnoma javoblari',
        'all_questions': 'Barcha savollar',
        'question': 'Savol',
        'answer': 'Javob',
        'detailed_answer': 'Batafsil javob',
        'phone_number': 'Telefon raqami',
        'additional_suggestions': 'Qo\'shimcha takliflar',
        'completion_status': 'Yakunlanish holati',
        'completed': 'Yakunlangan',
        'not_completed': 'Yakunlanmagan',
        'start_date': 'Boshlanish sanasi',
        'end_date': 'Yakunlanish sanasi'
    },
    'ru': {
        'dashboard': 'Панель управления',
        'users': 'Пользователи',
        'analytics': 'Аналитика',
        'settings': 'Настройки',
        'export_data': 'Экспорт данных',
        'logout': 'Выход',
        'total_users': 'Всего пользователей',
        'completed_surveys': 'Завершенные опросы',
        'completion_rate': 'Процент завершения',
        'users_who_started': 'Начавшие опрос',
        'bank_statistics': 'Статистика по банкам',
        'yes': 'Да',
        'no': 'Нет',
        'partially': 'Частично',
        'details': 'Подробнее',
        'information': 'Информация',
        'delete': 'Удалить',
        'back': 'Назад',
        'save': 'Сохранить',
        'change_password': 'Смена пароля',
        'old_password': 'Старый пароль',
        'new_password': 'Новый пароль',
        'confirm_password': 'Подтвердите новый пароль',
        'password_changed': 'Пароль успешно изменен',
        'password_error': 'Неверный пароль',
        'language': 'Язык',
        'percentage': 'Процент',
        'count': 'Количество',
        'total': 'Всего',
        'export_excel': 'Скачать в Excel',
        'people': 'человек',
        'other_bank': 'Другой банк',
        'bank_users': 'Пользователи банка',
        'view_details': 'Подробнее',
        'total_users_in_bank': 'Всего пользователей в банке',
        'completed_surveys_in_bank': 'Завершенные опросы в банке',
        'completion_rate_in_bank': 'Процент завершения в банке',
        'export_to_excel': 'Скачать в Excel',
        'back_to_dashboard': 'Вернуться в Dashboard',
        'bank_name': 'Название банка',
        'user_count': 'Количество пользователей',
        'survey_responses': 'Ответы на опрос',
        'all_questions': 'Все вопросы',
        'question': 'Вопрос',
        'answer': 'Ответ',
        'detailed_answer': 'Подробный ответ',
        'phone_number': 'Номер телефона',
        'additional_suggestions': 'Дополнительные предложения',
        'completion_status': 'Статус завершения',
        'completed': 'Завершено',
        'not_completed': 'Не завершено',
        'start_date': 'Дата начала',
        'end_date': 'Дата окончания'
    },
    'kar': {
        'dashboard': 'Баскару панели',
        'users': 'Пайдаланушылар',
        'analytics': 'Аналитика',
        'settings': 'Орнатулар',
        'export_data': 'Маглұматтарды жүктеу',
        'logout': 'Шығу',
        'total_users': 'Барлық пайдаланушылар',
        'completed_surveys': 'Аяқталған сауалнамалар',
        'completion_rate': 'Аяқталу пайызы',
        'users_who_started': 'Сауалнаманы бастағандар',
        'bank_statistics': 'Банктар бойынша статистика',
        'yes': 'Һа',
        'no': 'Йоқ',
        'partially': 'Жартылай',
        'details': 'Толық',
        'information': 'Мағлұмат',
        'delete': 'Өшіру',
        'back': 'Артқа',
        'save': 'Сақтау',
        'change_password': 'Парольді өзгерту',
        'old_password': 'Ескі пароль',
        'new_password': 'Жаңа пароль',
        'confirm_password': 'Жаңа парольді растаңыз',
        'password_changed': 'Пароль сәтті өзгертілді',
        'password_error': 'Пароль қате',
        'language': 'Тіл',
        'percentage': 'Пайыз',
        'count': 'Саны',
        'total': 'Барлығы',
        'export_excel': 'Excel-ге жүктеу',
        'people': 'адам',
        'other_bank': 'Басқа банк',
        'bank_users': 'Банк пайдаланушылары',
        'view_details': 'Толық',
        'total_users_in_bank': 'Банктегі барлық пайдаланушылар',
        'completed_surveys_in_bank': 'Банкте аяқталған сауалнамалар',
        'completion_rate_in_bank': 'Банкте аяқталу пайызы',
        'export_to_excel': 'Excel-ге жүктеу',
        'back_to_dashboard': 'Dashboard-қа қайту',
        'bank_name': 'Банк атауы',
        'user_count': 'Пайдаланушылар саны',
        'survey_responses': 'Сауалнама жауаптары',
        'all_questions': 'Барлық сұрақтар',
        'question': 'Сұрақ',
        'answer': 'Жауап',
        'detailed_answer': 'Толық жауап',
        'phone_number': 'Телефон нөмірі',
        'additional_suggestions': 'Қосымша ұсыныстар',
        'completion_status': 'Аяқталу жағдайы',
        'completed': 'Аяқталған',
        'not_completed': 'Аяқталмаған',
        'start_date': 'Басталу күні',
        'end_date': 'Аяқталу күні'
    }
}

# HTML ШАБЛОНЫ
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f7fb;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #4f46e5;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .login-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .form-group label {
            color: #374151;
            font-weight: 500;
            font-size: 14px;
        }
        
        .form-group input {
            padding: 12px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .login-button {
            background: #4f46e5;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
            margin-top: 10px;
        }
        
        .login-button:hover {
            background: #4338ca;
        }
        
        .error-message {
            color: #ef4444;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
            display: none;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">Survey Analytics</div>
        <div class="login-header">
            <h1>Admin Login</h1>
            <p>Enter your credentials to access the dashboard</p>
        </div>
        
        <form class="login-form" id="loginForm">
            <div class="form-group">
                <label for="login">Login</label>
                <input type="text" id="login" name="login" required placeholder="Enter your login">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter your password">
            </div>
            
            <button type="submit" class="login-button">Login</button>
            
            <div class="error-message" id="errorMessage">
                Invalid login or password
            </div>
        </form>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const errorMessage = document.getElementById('errorMessage');
            
            try {
                const response = await fetch('/auth', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    errorMessage.textContent = data.error || 'Invalid login or password';
                    errorMessage.style.display = 'block';
                }
            } catch (error) {
                errorMessage.textContent = 'Network error. Please try again.';
                errorMessage.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.dashboard }}</title>
    <!-- Используем CDN для Chart.js и плагинов -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: white;
            padding: 25px 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-title {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            color: #374151;
            text-decoration: none;
            transition: all 0.3s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #4f46e5;
            color: white;
        }

        .language-selector {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .lang-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            text-decoration: none;
            font-size: 12px;
        }

        .lang-btn.active {
            background: #4f46e5;
            color: white;
        }

        .main-content {
            flex: 1;
            padding: 30px;
            margin-left: 250px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1f2937;
            font-size: 28px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .logout-btn, .export-btn {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
        }

        .export-btn {
            background: #10b981;
            color: white;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .stat-card h3 {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 10px;
        }

        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 80px;
            column-gap: 25px;
            margin-bottom: 30px;
        }   

        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            height: 400px;
            position: relative;
        }

        .chart-card h3 {
            color: #1f2937;
            margin-bottom: 15px;
            font-size: 16px;
            height: 40px;
        }

        .chart-container {
            height: 300px;
            position: relative;
            width: 100%;
        }

        .chart-stats {
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
        }

        .stat-label {
            font-size: 12px;
            color: #6b7280;
            margin-top: 5px;
        }

        .bank-stats {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }

        .bank-stats h3 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 18px;
        }

        .bank-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .bank-item {
            padding: 15px;
            border-radius: 8px;
            background: #f9fafb;
            border-left: 4px solid #4f46e5;
        }

        .bank-name {
            font-weight: 600;
            color: #374151;
            margin-bottom: 5px;
        }

        .bank-count {
            color: #6b7280;
            font-size: 14px;
        }

        .no-data {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #6b7280;
            font-style: italic;
            font-size: 14px;
            text-align: center;
            z-index: 1;
        }

        .percentage-display {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #4f46e5;
            z-index: 10;
            display: none;
        }
        
        .percentage-display span {
            display: block;
            font-size: 14px;
            color: #6b7280;
            margin-top: 5px;
            font-weight: normal;
        }

        .bank-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .bank-cards-container {
            margin-top: 30px;
        }

        .bank-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .bank-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .bank-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-color: #4f46e5;
        }

        .bank-card.other-bank {
            border-color: #d1d5db;
            background: #f9fafb;
        }

        .bank-card.other-bank:hover {
            border-color: #9ca3af;
        }

        .bank-card-header {
            border-bottom: 2px solid #f3f4f6;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }

        .bank-card-title {
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
            text-align: center;
        }

        .bank-card-body {
            text-align: center;
        }

        .bank-card-count {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 5px;
        }

        .bank-card.other-bank .bank-card-count {
            color: #6b7280;
        }

        .bank-card-percentage {
            font-size: 14px;
            color: #6b7280;
            background: #f3f4f6;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Survey Analytics</div>
        
        <div class="nav-section">
            <div class="nav-title">{{ t.language }}</div>
            <div class="language-selector">
                <a href="/set_language/uz" class="lang-btn {% if current_lang == "uz" %}active{% endif %}">🇺🇿 UZ</a>
                <a href="/set_language/ru" class="lang-btn {% if current_lang == "ru" %}active{% endif %}">🇷🇺 RU</a>
                <a href="/set_language/kar" class="lang-btn {% if current_lang == "kar" %}active{% endif %}">🇺🇿 ҚАР</a>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">Main Menu</div>
            <a href="/dashboard" class="nav-item active">
                {{ t.dashboard }}
            </a>
            <a href="/users" class="nav-item">
                {{ t.users }}
            </a>
            <a href="/settings" class="nav-item">
                {{ t.settings }}
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">Export</div>
            <a href="/export/index.txt" class="nav-item">{{ t.export_data }}</a>
        </div>

        <a href="/logout" class="nav-item" style="margin-top: auto;">
            {{ t.logout }}
        </a>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>{{ t.dashboard }}</h1>
            <div class="header-actions">
                <a href="/export/index.txt" class="export-btn">{{ t.export_data }}</a>
                <a href="/logout" class="logout-btn">{{ t.logout }}</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ t.total_users }}</h3>
                <div class="stat-value" id="totalUsers">{{ total_users }}</div>
                <div class="stat-change positive">
                    {{ t.users_who_started }}
                </div>
            </div>
            <div class="stat-card">
                <h3>{{ t.completed_surveys }}</h3>
                <div class="stat-value" id="completedSurveys">{{ completed }}</div>
                <div class="stat-change positive" id="completionRate">
                    {{ ((completed/total_users*100) if total_users > 0 else 0)|round(2) }}% {{ t.completion_rate }}
                </div>
            </div>
        </div>

        <div class="bank-stats">
            <div class="bank-header">
                <h3>{{ t.bank_statistics }} (Q1)</h3>
                <div>
                    <a href="/export/bank_stats" class="export-btn" style="padding: 8px 16px; font-size: 14px;">
                        {{ t.export_excel }}
                    </a>
                </div>
            </div>
            
            <div class="chart-container" style="height: 300px; margin-bottom: 20px;">
                <canvas id="bankChart"></canvas>
            </div>
            
            <!-- 13 банктың карточкалары -->
            <div class="bank-cards-container">
                <div class="bank-cards-grid">
                    {% set bank_dict = bank_stats.detailed %}
                    {% set all_banks = [
                        'Инфин банк', 'Асака банк', 'Халк банк', 'Алоқа банк', 
                        'Капитал банк', 'Ипотека банк', 'Агробанк', 'Миллий банк',
                        'Hamkor банк', 'Микрокредитбанк', 'Туран банк', 'БРБ банк', 'SQB банк'
                    ] %}
                    
                    {% for bank_name in all_banks %}
                    <div class="bank-card" onclick="viewBankUsers('{{ bank_name }}')">
                        <div class="bank-card-header">
                            <div class="bank-card-title">{{ bank_name }}</div>
                        </div>
                        <div class="bank-card-body">
                            <div class="bank-card-count">
                                {{ bank_dict.get(bank_name, 0) }} {{ t.people }}
                            </div>
                            <div class="bank-card-percentage">
                                {% if bank_stats.total > 0 %}
                                    {{ ((bank_dict.get(bank_name, 0)/bank_stats.total*100)|round(1)) }}%
                                {% else %}
                                    0%
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                    
                    <!-- Бошқа банк карточкасы -->
                    <div class="bank-card other-bank" onclick="viewBankUsers('Бошқа банк')">
                        <div class="bank-card-header">
                            <div class="bank-card-title">{{ t.other_bank }}</div>
                        </div>
                        <div class="bank-card-body">
                            <div class="bank-card-count">
                                {{ bank_dict.get('Бошқа банк', 0) }} {{ t.people }}
                            </div>
                            <div class="bank-card-percentage">
                                {% if bank_stats.total > 0 %}
                                    {{ ((bank_dict.get('Бошқа банк', 0)/bank_stats.total*100)|round(1)) }}%
                                {% else %}
                                    0%
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-card">
                <h3>Savol 2: {{ t.yes }}/{{ t.no }} nisbati</h3>
                <div class="chart-container">
                    <canvas id="q2Chart"></canvas>
                    <div id="q2Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q2Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 3: {{ t.yes }}/{{ t.no }}/{{ t.partially }}</h3>
                <div class="chart-container">
                    <canvas id="q3Chart"></canvas>
                    <div id="q3Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q3Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 4: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q4Chart"></canvas>
                    <div id="q4Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q4Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 5: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q5Chart"></canvas>
                    <div id="q5Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q5Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 6: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q6Chart"></canvas>
                    <div id="q6Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q6Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 8: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q8Chart"></canvas>
                    <div id="q8Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q8Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 9: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q9Chart"></canvas>
                    <div id="q9Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q9Stats"></div>
            </div>
            <div class="chart-card">
                <h3>Savol 10: {{ t.yes }}/{{ t.no }}</h3>
                <div class="chart-container">
                    <canvas id="q10Chart"></canvas>
                    <div id="q10Percentage" class="percentage-display"></div>
                </div>
                <div class="chart-stats" id="q10Stats"></div>
            </div>
        </div>
    </div>

    <script>
        // Регистрируем плагин для Chart.js
        if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
            Chart.register(ChartDataLabels);
        } else {
            console.error('Chart.js or ChartDataLabels not loaded');
        }

        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();
                
                if (!data) {
                    throw new Error('No data received from server');
                }
                
                document.getElementById('totalUsers').textContent = data.general.total;
                document.getElementById('completedSurveys').textContent = data.general.completed;
                
                const completionRate = data.general.total > 0 
                    ? Math.round((data.general.completed / data.general.total) * 100) 
                    : 0;
                document.getElementById('completionRate').textContent = 
                    `${completionRate}% {{ t.completion_rate }}`;
                
                // Создаем диаграммы для вопросов
                const questions = ['q2', 'q3', 'q4', 'q5', 'q6', 'q8', 'q9', 'q10'];
                questions.forEach(q => {
                    if (data.questions[q]) {
                        try {
                            createChart(`${q}Chart`, `${q}Percentage`, `${q}Stats`, data.questions[q]);
                        } catch (chartErr) {
                            console.error(`Error creating chart ${q}:`, chartErr);
                            const container = document.getElementById(`${q}Chart`);
                            if (container && container.parentElement) {
                                container.parentElement.innerHTML = '<div style="color:red; text-align:center; padding:20px;">Error rendering chart</div>';
                            }
                        }
                    }
                });

                // Создаем диаграмму для банков
                if (data.bank_stats && data.bank_stats.banks && data.bank_stats.banks.length > 0) {
                    try {
                        createBankChart('bankChart', data.bank_stats);
                    } catch (err) {
                        console.error('Error creating bank chart:', err);
                        const canvas = document.getElementById('bankChart');
                        if (canvas && canvas.parentElement) {
                            canvas.parentElement.innerHTML = '<div style="color:red; text-align:center; padding:20px;">Error rendering bank chart</div>';
                        }
                    }
                }
                
            } catch (error) {
                console.error('Error loading statistics:', error);
                const grid = document.querySelector('.charts-container');
                if (grid) {
                    grid.insertAdjacentHTML('beforebegin', '<div style="background:red;color:white;padding:15px;margin-bottom:20px;border-radius:5px;">Failed to load statistics: ' + error.message + '</div>');
                }
            }
        }
        
        function createChart(canvasId, percentageId, statsId, questionData) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.error(`Canvas element not found: ${canvasId}`);
                return;
            }
            
            // Удаляем предыдущую диаграмму если есть
            const existingChart = Chart.getChart(canvas);
            if (existingChart) {
                existingChart.destroy();
            }
            
            // Проверяем данные
            if (!questionData || !questionData.labels || !questionData.data) {
                console.error(`Invalid data for chart ${canvasId}:`, questionData);
                canvas.parentElement.innerHTML = '<div class="no-data">No data available</div>';
                return;
            }
            
            const total = questionData.data.reduce((a, b) => a + b, 0);
            if (total === 0) {
                canvas.parentElement.innerHTML = '<div class="no-data">No data available</div>';
                return;
            }
            
            // Цвета для диаграмм
            const colorMap = {
                'ha': '#ef4444', 
                'yoq': '#10b981', 
                'qisman': '#f59e0b',
                'да': '#ef4444', 
                'нет': '#10b981', 
                'частично': '#f59e0b',
                'һа': '#ef4444', 
                'йоқ': '#10b981', 
                'жартылай': '#f59e0b'
            };
            
            // Подготавливаем цвета
            const backgroundColors = questionData.labels.map(label => {
                const lowerLabel = String(label).toLowerCase().trim();
                for (const [key, color] of Object.entries(colorMap)) {
                    if (lowerLabel.includes(key)) {
                        return color;
                    }
                }
                return '#4f46e5';
            });
            
            try {
                // Создаем диаграмму
                new Chart(canvas, {
                    type: 'doughnut',
                    data: {
                        labels: questionData.labels,
                        datasets: [{
                            data: questionData.data,
                            backgroundColor: backgroundColors,
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    padding: 15,
                                    font: {
                                        size: 12
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            },
                            datalabels: {
                                color: '#ffffff',
                                font: {
                                    weight: 'bold',
                                    size: 14
                                },
                                formatter: (value) => {
                                    const percentage = ((value / total) * 100).toFixed(0);
                                    return percentage >= 10 ? `${percentage}%` : '';
                                }
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });
                
                // Показываем общее количество
                const percentageElement = document.getElementById(percentageId);
                if (percentageElement) {
                    percentageElement.style.display = 'block';
                    percentageElement.innerHTML = `${total}<span>Jami</span>`;
                }
                
                // Обновляем статистику
                const statsContainer = document.getElementById(statsId);
                if (statsContainer) {
                    statsContainer.innerHTML = '';
                    
                    questionData.labels.forEach((label, index) => {
                        const value = questionData.data[index];
                        const percentage = ((value / total) * 100).toFixed(1);
                        
                        const statItem = document.createElement('div');
                        statItem.className = 'stat-item';
                        statItem.innerHTML = `
                            <div class="stat-number" style="color: ${backgroundColors[index]}">${value}</div>
                            <div class="stat-label">${label}</div>
                            <div class="stat-label" style="font-size: 10px;">${percentage}%</div>
                        `;
                        
                        statsContainer.appendChild(statItem);
                    });
                }
                
            } catch (error) {
                console.error(`Error creating chart ${canvasId}:`, error);
                canvas.parentElement.innerHTML = '<div class="no-data">Chart error</div>';
            }
        }

        function createBankChart(canvasId, bankData) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            
            // Удаляем предыдущую диаграмму
            const existingChart = Chart.getChart(canvas);
            if (existingChart) existingChart.destroy();
            
            // Сортируем данные по количеству (убывание)
            const sortedData = bankData.banks.map((bank, index) => ({
                bank,
                count: bankData.counts[index]
            })).sort((a, b) => b.count - a.count);
            
            const sortedBanks = sortedData.map(item => item.bank);
            const sortedCounts = sortedData.map(item => item.count);
            
            try {
                new Chart(canvas, {
                    type: 'bar',
                    data: {
                        labels: sortedBanks,
                        datasets: [{
                            label: 'Foydalanuvchilar soni',
                            data: sortedCounts,
                            backgroundColor: '#4f46e5',
                            borderColor: '#4338ca',
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { 
                                display: true,
                                position: 'bottom',
                                labels: {
                                    font: {
                                        size: 12
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const percentage = ((context.raw / bankData.total) * 100).toFixed(1);
                                        return `${context.raw} ta (${percentage}%)`;
                                    }
                                }
                            },
                            datalabels: {
                                anchor: 'end',
                                align: 'end',
                                color: '#374151',
                                font: { 
                                    weight: 'bold',
                                    size: 11 
                                },
                                formatter: function(value) {
                                    const percentage = ((value / bankData.total) * 100).toFixed(1);
                                    return `${value} (${percentage}%)`;
                                }
                            }
                        },
                        scales: {
                            x: { 
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1,
                                    callback: function(value) {
                                        return Number.isInteger(value) ? value : '';
                                    }
                                }
                            },
                            y: {
                                ticks: {
                                    font: {
                                        size: 11
                                    }
                                }
                            }
                        }
                    },
                    plugins: [ChartDataLabels]
                });
            } catch (error) {
                console.error('Error creating bank chart:', error);
                canvas.parentElement.innerHTML = '<div class="no-data">Bank chart error</div>';
            }
        }
        
        // Банк карточкасын басқанда банктың пайдаланушыларын көрсету
        function viewBankUsers(bankName) {
            window.location.href = `/bank_users/${encodeURIComponent(bankName)}`;
        }
        
        // Загружаем статистику при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            // Даем время на загрузку Chart.js
            setTimeout(loadStatistics, 100);
        });
        
        // Обновляем статистику каждые 30 секунд
        setInterval(loadStatistics, 30000);
    </script>
</body>
</html>
'''

USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.users }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: white;
            padding: 25px 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-title {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            color: #374151;
            text-decoration: none;
            transition: all 0.3s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #4f46e5;
            color: white;
        }

        .language-selector {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .lang-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            text-decoration: none;
            font-size: 12px;
        }

        .lang-btn.active {
            background: #4f46e5;
            color: white;
        }

        .main-content {
            flex: 1;
            padding: 30px;
            margin-left: 250px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1f2937;
            font-size: 28px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .logout-btn, .export-btn {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
        }

        .export-btn {
            background: #10b981;
            color: white;
        }

        .users-table {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }

        .table-header {
            display: grid;
            grid-template-columns: 50px 100px 150px 150px 100px 120px 120px 100px 150px;
            padding: 20px;
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
            border-bottom: 1px solid #e5e7eb;
        }

        .table-row {
            display: grid;
            grid-template-columns: 50px 100px 150px 150px 100px 120px 120px 100px 150px;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
            align-items: center;
        }

        .table-row:hover {
            background: #f9fafb;
        }

        .completed-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .completed-yes {
            background: #10b981;
            color: white;
        }

        .completed-no {
            background: #ef4444;
            color: white;
        }

        .action-btn {
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 500;
            margin-right: 5px;
            display: inline-block;
        }

        .view-btn {
            background: #4f46e5;
            color: white;
        }

        .download-btn {
            background: #10b981;
            color: white;
        }

        .delete-btn {
            background: #ef4444;
            color: white;
            border: none;
            cursor: pointer;
            font-family: inherit;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Survey Analytics</div>
        
        <div class="nav-section">
            <div class="nav-title">{{ t.language }}</div>
            <div class="language-selector">
                <a href="/set_language/uz" class="lang-btn {% if current_lang == "uz" %}active{% endif %}">🇺🇿 UZ</a>
                <a href="/set_language/ru" class="lang-btn {% if current_lang == "ru" %}active{% endif %}">🇷🇺 RU</a>
                <a href="/set_language/kar" class="lang-btn {% if current_lang == "kar" %}active{% endif %}">🇺🇿 ҚАР</a>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">Main Menu</div>
            <a href="/dashboard" class="nav-item">
                {{ t.dashboard }}
            </a>
            <a href="/users" class="nav-item active">
                {{ t.users }}
            </a>
            <a href="/settings" class="nav-item">
                {{ t.settings }}
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">Export</div>
            <a href="/export/index.txt" class="nav-item">{{ t.export_data }}</a>
        </div>

        <a href="/logout" class="nav-item" style="margin-top: auto;">
            {{ t.logout }}
        </a>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>{{ t.users }}</h1>
            <div class="header-actions">
                <a href="/export/index.txt" class="export-btn">{{ t.export_data }}</a>
                <a href="/logout" class="logout-btn">{{ t.logout }}</a>
            </div>
        </div>

        <div class="users-table">
            <div class="table-header">
                <div>ID</div>
                <div>Telegram ID</div>
                <div>Username</div>
                <div>Name</div>
                <div>Language</div>
                <div>Started</div>
                <div>Completed</div>
                <div>Status</div>
                <div>Actions</div>
            </div>
            
            {% for user in users %}
            <div class="table-row" id="user-{{ user.id }}">
                <div>{{ user.id }}</div>
                <div>{{ user.tg_id }}</div>
                <div>@{{ user.username or 'N/A' }}</div>
                <div>{{ user.first_name or '' }} {{ user.last_name or '' }}</div>
                <div>{{ user.language }}</div>
                <div>{{ user.started_at }}</div>
                <div>{{ user.completed_at or 'N/A' }}</div>
                <div>
                    <span class="completed-badge {% if user.completed %}completed-yes{% else %}completed-no{% endif %}">
                        {% if user.completed %}{{ t.yes }}{% else %}{{ t.no }}{% endif %}
                    </span>
                </div>
                <div>
                    <a href="/user/{{ user.id }}" class="action-btn view-btn">{{ t.details }}</a>
                    <a href="/user/{{ user.id }}/download" class="action-btn download-btn">{{ t.export_data }}</a>
                    <button onclick="deleteUser({{ user.id }})" class="delete-btn">{{ t.delete }}</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        async function deleteUser(userId) {
            if (!confirm('Bu foydalanuvchini o\'chirmoqchimisiz?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/delete_user/${userId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById(`user-${userId}`).remove();
                    alert('Foydalanuvchi muvaffaqiyatli o\'chirildi');
                } else {
                    alert('Xatolik yuz berdi: ' + data.error);
                }
            } catch (error) {
                alert('Tarmoq xatosi');
            }
        }
    </script>
</body>
</html>
'''

USER_DETAILS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Details</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: white;
            padding: 25px 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-title {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            color: #374151;
            text-decoration: none;
            transition: all 0.3s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #4f46e5;
            color: white;
        }

        .language-selector {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .lang-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            text-decoration: none;
            font-size: 12px;
        }

        .lang-btn.active {
            background: #4f46e5;
            color: white;
        }

        .main-content {
            flex: 1;
            padding: 30px;
            margin-left: 250px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1f2937;
            font-size: 28px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .logout-btn, .export-btn, .back-btn {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
        }

        .export-btn {
            background: #10b981;
            color: white;
        }

        .back-btn {
            background: #6b7280;
            color: white;
        }

        .user-info {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }

        .user-info h2 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 10px;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .info-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .info-label {
            color: #6b7280;
            font-size: 14px;
            font-weight: 500;
        }

        .info-value {
            color: #1f2937;
            font-size: 16px;
            font-weight: 600;
        }

        .responses-section {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .responses-section h2 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 10px;
        }

        .response-item {
            margin-bottom: 25px;
            padding-bottom: 25px;
            border-bottom: 1px solid #e5e7eb;
        }

        .response-item:last-child {
            border-bottom: none;
        }

        .question {
            color: #374151;
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .answer {
            color: #4f46e5;
            background: #f5f7fb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4f46e5;
            white-space: pre-wrap;
        }

        .no-response {
            color: #6b7280;
            font-style: italic;
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #d1d5db;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Survey Analytics</div>
        
        <div class="nav-section">
            <div class="nav-title">{{ t.language }}</div>
            <div class="language-selector">
                <a href="/set_language/uz" class="lang-btn {% if current_lang == "uz" %}active{% endif %}">🇺🇿 UZ</a>
                <a href="/set_language/ru" class="lang-btn {% if current_lang == "ru" %}active{% endif %}">🇷🇺 RU</a>
                <a href="/set_language/kar" class="lang-btn {% if current_lang == "kar" %}active{% endif %}">🇺🇿 ҚАР</a>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">Main Menu</div>
            <a href="/dashboard" class="nav-item">
                {{ t.dashboard }}
            </a>
            <a href="/users" class="nav-item">
                {{ t.users }}
            </a>
            <a href="/settings" class="nav-item">
                {{ t.settings }}
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">Export</div>
            <a href="/export/index.txt" class="nav-item">{{ t.export_data }}</a>
        </div>

        <a href="/logout" class="nav-item" style="margin-top: auto;">
            {{ t.logout }}
        </a>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>{{ t.information }}</h1>
            <div class="header-actions">
                <a href="/users" class="back-btn">{{ t.back }}</a>
                <a href="/user/{{ user.id }}/download" class="export-btn">{{ t.export_data }}</a>
                <a href="/logout" class="logout-btn">{{ t.logout }}</a>
            </div>
        </div>

        <div class="user-info">
            <h2>User Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">ID</div>
                    <div class="info-value">{{ user.id }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Telegram ID</div>
                    <div class="info-value">{{ user.tg_id }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Username</div>
                    <div class="info-value">@{{ user.username or 'N/A' }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Full Name</div>
                    <div class="info-value">{{ user.first_name or '' }} {{ user.last_name or '' }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Language</div>
                    <div class="info-value">{{ user.language }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Started At</div>
                    <div class="info-value">{{ user.started_at }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Completed</div>
                    <div class="info-value">
                        <span style="color: {% if user.completed %}#10b981{% else %}#ef4444{% endif %}; font-weight: bold;">
                            {% if user.completed %}{{ t.yes }}{% else %}{{ t.no }}{% endif %}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div class="responses-section">
            <h2>Survey Responses</h2>
            
            {% if responses %}
            <div class="response-item">
                <div class="question">Q1: Qaysi bankda ishlaysiz?</div>
                <div class="answer">{{ responses.q1 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q2: Bankda korruptsiya bormi?</div>
                <div class="answer">{{ responses.q2 or 'No response' }}</div>
                {% if responses.q2_text %}
                <div style="margin-top: 10px;">
                    <div class="question">Q2 (batafsil):</div>
                    <div class="answer">{{ responses.q2_text }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="response-item">
                <div class="question">Q3: Jamoa muhitidan qoniqasizmi?</div>
                <div class="answer">{{ responses.q3 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q4: Noqonuniy topshiriqlar bormi?</div>
                <div class="answer">{{ responses.q4 or 'No response' }}</div>
                {% if responses.q4_text %}
                <div style="margin-top: 10px;">
                    <div class="question">Q4 (batafsil):</div>
                    <div class="answer">{{ responses.q4_text }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="response-item">
                <div class="question">Q5: Ichki hujjatlar buzilishi bormi?</div>
                <div class="answer">{{ responses.q5 or 'No response' }}</div>
                {% if responses.q5_text %}
                <div style="margin-top: 10px;">
                    <div class="question">Q5 (batafsil):</div>
                    <div class="answer">{{ responses.q5_text }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="response-item">
                <div class="question">Q6: Rotatsiyada manfaatlar to'qnashuvi bormi?</div>
                <div class="answer">{{ responses.q6 or 'No response' }}</div>
                {% if responses.q6_text %}
                <div style="margin-top: 10px;">
                    <div class="question">Q6 (batafsil):</div>
                    <div class="answer">{{ responses.q6_text }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="response-item">
                <div class="question">Q7: Ishga qabul tizimi (1-10)</div>
                <div class="answer">{{ responses.q7 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q8: Xizmat vazifalarida korruptsiya bormi?</div>
                <div class="answer">{{ responses.q8 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q9: Pul yig'imlari tashkil etiladimi?</div>
                <div class="answer">{{ responses.q9 or 'No response' }}</div>
                {% if responses.q9_text %}
                <div style="margin-top: 10px;">
                    <div class="question">Q9 (batafsil):</div>
                    <div class="answer">{{ responses.q9_text }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="response-item">
                <div class="question">Q10: Adolatsiz qarorlar bormi?</div>
                <div class="answer">{{ responses.q10 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q11: Telefon raqami</div>
                <div class="answer">{{ responses.q11 or 'No response' }}</div>
            </div>
            
            <div class="response-item">
                <div class="question">Q12: Qo'shimcha takliflar</div>
                <div class="answer">{{ responses.q12 or 'No response' }}</div>
            </div>
            {% else %}
            <div class="no-response">No survey responses found for this user.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

SETTINGS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.settings }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: white;
            padding: 25px 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-title {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            color: #374151;
            text-decoration: none;
            transition: all 0.3s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #4f46e5;
            color: white;
        }

        .language-selector {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .lang-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            text-decoration: none;
            font-size: 12px;
        }

        .lang-btn.active {
            background: #4f46e5;
            color: white;
        }

        .main-content {
            flex: 1;
            padding: 30px;
            margin-left: 250px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1f2937;
            font-size: 28px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .logout-btn, .export-btn {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
        }

        .export-btn {
            background: #10b981;
            color: white;
        }

        .settings-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .settings-section {
            margin-bottom: 40px;
        }

        .settings-section h2 {
            color: #1f2937;
            margin-bottom: 20px;
            font-size: 20px;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 10px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 20px;
        }

        .form-group label {
            color: #374151;
            font-weight: 500;
            font-size: 14px;
        }

        .form-group input {
            padding: 12px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .save-button {
            background: #4f46e5;
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }

        .save-button:hover {
            background: #4338ca;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: none;
        }

        .alert-success {
            background: #10b981;
            color: white;
        }

        .alert-error {
            background: #ef4444;
            color: white;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Survey Analytics</div>
        
        <div class="nav-section">
            <div class="nav-title">{{ t.language }}</div>
            <div class="language-selector">
                <a href="/set_language/uz" class="lang-btn {% if current_lang == "uz" %}active{% endif %}">🇺🇿 UZ</a>
                <a href="/set_language/ru" class="lang-btn {% if current_lang == "ru" %}active{% endif %}">🇷🇺 RU</a>
                <a href="/set_language/kar" class="lang-btn {% if current_lang == "kar" %}active{% endif %}">🇺🇿 ҚАР</a>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">Main Menu</div>
            <a href="/dashboard" class="nav-item">
                {{ t.dashboard }}
            </a>
            <a href="/users" class="nav-item">
                {{ t.users }}
            </a>
            <a href="/settings" class="nav-item active">
                {{ t.settings }}
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">Export</div>
            <a href="/export/index.txt" class="nav-item">{{ t.export_data }}</a>
        </div>

        <a href="/logout" class="nav-item" style="margin-top: auto;">
            {{ t.logout }}
        </a>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>{{ t.settings }}</h1>
            <div class="header-actions">
                <a href="/export/index.txt" class="export-btn">{{ t.export_data }}</a>
                <a href="/logout" class="logout-btn">{{ t.logout }}</a>
            </div>
        </div>

        <div class="settings-container">
            <div id="successAlert" class="alert alert-success" style="display: none;">
                {{ t.password_changed }}
            </div>
            <div id="errorAlert" class="alert alert-error" style="display: none;">
                {{ t.password_error }}
            </div>
            
            <div class="settings-section">
                <h2>{{ t.change_password }}</h2>
                <form method="POST" action="/settings" id="passwordForm">
                    <div class="form-group">
                        <label for="old_password">{{ t.old_password }}</label>
                        <input type="password" id="old_password" name="old_password" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="new_password">{{ t.new_password }}</label>
                        <input type="password" id="new_password" name="new_password" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="confirm_password">{{ t.confirm_password }}</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                    </div>
                    
                    <button type="submit" class="save-button">{{ t.save }}</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('passwordForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const successAlert = document.getElementById('successAlert');
            const errorAlert = document.getElementById('errorAlert');
            
            try {
                const response = await fetch('/settings', {
                    method: 'POST',
                    body: formData
                });
                
                // Since Flask will redirect on POST, we'll handle message via session
                // Reload the page to show flash messages
                window.location.reload();
                
            } catch (error) {
                errorAlert.textContent = 'Network error. Please try again.';
                errorAlert.style.display = 'block';
                successAlert.style.display = 'none';
            }
        });
        
        // Check for flash messages in URL parameters
        window.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('success')) {
                document.getElementById('successAlert').style.display = 'block';
            }
            if (urlParams.get('error')) {
                document.getElementById('errorAlert').style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

BANK_USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ bank_name }} - {{ t.bank_users }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 250px;
            background: white;
            padding: 25px 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4f46e5;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .nav-section {
            margin-bottom: 30px;
        }

        .nav-title {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 8px;
            color: #374151;
            text-decoration: none;
            transition: all 0.3s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #4f46e5;
            color: white;
        }

        .language-selector {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .lang-btn {
            flex: 1;
            text-align: center;
            padding: 8px;
            border-radius: 6px;
            background: #f3f4f6;
            color: #6b7280;
            text-decoration: none;
            font-size: 12px;
        }

        .lang-btn.active {
            background: #4f46e5;
            color: white;
        }

        .main-content {
            flex: 1;
            padding: 30px;
            margin-left: 250px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #1f2937;
            font-size: 28px;
        }

        .header h2 {
            color: #6b7280;
            font-size: 16px;
            font-weight: normal;
            margin-top: 5px;
        }

        .header-actions {
            display: flex;
            gap: 10px;
        }

        .logout-btn, .export-btn, .back-btn {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
        }

        .export-btn {
            background: #10b981;
            color: white;
        }

        .back-btn {
            background: #6b7280;
            color: white;
        }

        .export-excel-btn {
            background: #0ea5e9;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            border: none;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .stats-container {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .stat-item {
            text-align: center;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #4f46e5;
        }

        .stat-label {
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 5px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #1f2937;
        }

        .users-table-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
            margin-bottom: 30px;
        }

        .table-header {
            display: grid;
            grid-template-columns: 50px 150px 100px minmax(100px, 1fr) 100px 120px 120px 120px 120px 120px 100px 100px 100px;
            padding: 20px;
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
            border-bottom: 1px solid #e5e7eb;
            font-size: 12px;
            gap: 10px;
        }

        .table-row {
            display: grid;
            grid-template-columns: 50px 150px 100px minmax(100px, 1fr) 100px 120px 120px 120px 120px 120px 100px 100px 100px;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
            align-items: start;
            font-size: 12px;
            gap: 10px;
        }

        .table-row:hover {
            background: #f9fafb;
        }

        .question-header {
            background: #f3f4f6;
            text-align: center;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
        }

        .answer-cell {
            padding: 5px;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 100px;
            overflow-y: auto;
            background: #f9fafb;
            border-radius: 4px;
            border: 1px solid #e5e7eb;
        }

        .no-data {
            color: #6b7280;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }

        .user-info {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .username {
            font-weight: bold;
            color: #1f2937;
        }

        .tg-id {
            color: #6b7280;
            font-size: 11px;
        }

        .view-details-btn {
            background: #4f46e5;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            display: inline-block;
            text-align: center;
            width: 100%;
        }

        @media (max-width: 1600px) {
            .table-header, .table-row {
                overflow-x: auto;
                display: block;
                white-space: nowrap;
            }
            
            .table-header > div, .table-row > div {
                display: inline-block;
                width: 150px;
                vertical-align: top;
                white-space: normal;
                padding: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Survey Analytics</div>
        
        <div class="nav-section">
            <div class="nav-title">{{ t.language }}</div>
            <div class="language-selector">
                <a href="/set_language/uz" class="lang-btn {% if current_lang == "uz" %}active{% endif %}">🇺🇿 UZ</a>
                <a href="/set_language/ru" class="lang-btn {% if current_lang == "ru" %}active{% endif %}">🇷🇺 RU</a>
                <a href="/set_language/kar" class="lang-btn {% if current_lang == "kar" %}active{% endif %}">🇺🇿 ҚАР</a>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-title">Main Menu</div>
            <a href="/dashboard" class="nav-item">
                {{ t.dashboard }}
            </a>
            <a href="/users" class="nav-item">
                {{ t.users }}
            </a>
            <a href="/settings" class="nav-item">
                {{ t.settings }}
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-title">Export</div>
            <a href="/export/index.txt" class="nav-item">{{ t.export_data }}</a>
        </div>

        <a href="/logout" class="nav-item" style="margin-top: auto;">
            {{ t.logout }}
        </a>
    </div>

    <div class="main-content">
        <div class="header">
            <div>
                <h1>{{ bank_name }}</h1>
                <h2>{{ users|length }} {{ t.people }}</h2>
            </div>
            <div class="header-actions">
                <a href="/dashboard" class="back-btn">{{ t.back }}</a>
                <a href="/export/bank_users_excel/{{ bank_name|urlencode }}" class="export-excel-btn">
                    {{ t.export_to_excel }}
                </a>
                <a href="/logout" class="logout-btn">{{ t.logout }}</a>
            </div>
        </div>

        <div class="stats-container">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">{{ t.total_users_in_bank }}</div>
                    <div class="stat-value">{{ users|length }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">{{ t.completed_surveys_in_bank }}</div>
                    <div class="stat-value">{{ completed_count }}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">{{ t.completion_rate_in_bank }}</div>
                    <div class="stat-value">
                        {% if users|length > 0 %}
                            {{ ((completed_count/users|length*100)|round(1)) }}%
                        {% else %}
                            0%
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <div class="users-table-container">
            <div class="table-header">
                <div>ID</div>
                <div>{{ t.information }}</div>
                <div>{{ t.language }}</div>
                <div>Q1: {{ t.bank_name }}</div>
                <div>Q2: Korruptsiya</div>
                <div>Q3: Jamoa muhiti</div>
                <div>Q4: Noqonuniy topshiriqlar</div>
                <div>Q5: Ichki hujjatlar</div>
                <div>Q6: Rotatsiya</div>
                <div>Q7: Ishga qabul (1-10)</div>
                <div>Q8: Xizmat vazifalarida korruptsiya</div>
                <div>Q9: Pul yig'imlari</div>
                <div>Q10: Adolatsiz qarorlar</div>
            </div>
            
            {% for user in users %}
            <div class="table-row">
                <div>{{ user.id }}</div>
                <div class="user-info">
                    <div class="username">{{ user.first_name }} {{ user.last_name }}</div>
                    <div class="tg-id">@{{ user.username or 'N/A' }}</div>
                    <div class="tg-id">ID: {{ user.tg_id }}</div>
                    <a href="/user/{{ user.id }}" class="view-details-btn">{{ t.view_details }}</a>
                </div>
                <div>{{ user.language }}</div>
                <div class="answer-cell">{{ user.q1 or '-' }}</div>
                <div class="answer-cell">
                    {{ user.q2 or '-' }}
                    {% if user.q2_text %}
                    <br><small style="color: #6b7280;">{{ user.q2_text[:50] }}{% if user.q2_text|length > 50 %}...{% endif %}</small>
                    {% endif %}
                </div>
                <div class="answer-cell">{{ user.q3 or '-' }}</div>
                <div class="answer-cell">
                    {{ user.q4 or '-' }}
                    {% if user.q4_text %}
                    <br><small style="color: #6b7280;">{{ user.q4_text[:50] }}{% if user.q4_text|length > 50 %}...{% endif %}</small>
                    {% endif %}
                </div>
                <div class="answer-cell">
                    {{ user.q5 or '-' }}
                    {% if user.q5_text %}
                    <br><small style="color: #6b7280;">{{ user.q5_text[:50] }}{% if user.q5_text|length > 50 %}...{% endif %}</small>
                    {% endif %}
                </div>
                <div class="answer-cell">
                    {{ user.q6 or '-' }}
                    {% if user.q6_text %}
                    <br><small style="color: #6b7280;">{{ user.q6_text[:50] }}{% if user.q6_text|length > 50 %}...{% endif %}</small>
                    {% endif %}
                </div>
                <div class="answer-cell">{{ user.q7 or '-' }}</div>
                <div class="answer-cell">{{ user.q8 or '-' }}</div>
                <div class="answer-cell">
                    {{ user.q9 or '-' }}
                    {% if user.q9_text %}
                    <br><small style="color: #6b7280;">{{ user.q9_text[:50] }}{% if user.q9_text|length > 50 %}...{% endif %}</small>
                    {% endif %}
                </div>
                <div class="answer-cell">{{ user.q10 or '-' }}</div>
            </div>
            {% endfor %}
            
            {% if not users %}
            <div class="no-data">
                Бұл банкта жұмыс істейтін пайдаланушылар табылмады
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()
    
    # Создаем таблицу users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language TEXT,
        started_at TEXT,
        completed BOOLEAN DEFAULT 0
    )
    ''')
    
    # Создаем таблицу responses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        q1 TEXT,
        q2 TEXT,
        q2_text TEXT,
        q3 TEXT,
        q4 TEXT,
        q4_text TEXT,
        q5 TEXT,
        q5_text TEXT,
        q6 TEXT,
        q6_text TEXT,
        q7 TEXT,
        q8 TEXT,
        q9 TEXT,
        q9_text TEXT,
        q10 TEXT,
        q11 TEXT,
        q12 TEXT,
        completed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных успешно инициализирована")

def get_translation():
    lang = session.get('admin_language', 'uz')
    return TRANSLATIONS.get(lang, TRANSLATIONS['uz'])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('survey.db')
    conn.row_factory = sqlite3.Row
    return conn

def classify_bank(q1_text):
    """Банкты классификациялау функциясы"""
    if not q1_text:
        return 'Бошқа банк'
    
    text = q1_text.lower().strip()
    
    if any(keyword in text for keyword in ['инфин', 'infin', 'infbank', 'infın', 'инфинбанк']):
        return 'Инфин банк'
    elif any(keyword in text for keyword in ['асака', 'asaka', 'асак', 'asakabank', 'асакa']):
        return 'Асака банк'
    elif any(keyword in text for keyword in ['халк', 'halq', 'xalq', 'xalk', 'халқ', 'xalqbank']):
        return 'Халк банк'
    elif any(keyword in text for keyword in ['алоқа', 'aloqa', 'алоқа', 'аlok', 'aloqabank', 'алоқабанк']):
        return 'Алоқа банк'
    elif any(keyword in text for keyword in ['капитал', 'kapital', 'kapit', 'kapitalbank', 'капиталбанк']):
        return 'Капитал банк'
    elif any(keyword in text for keyword in ['ипотека', 'ipoteka', 'ipotek', 'ipotekabank', 'ипотекабанк']):
        return 'Ипотека банк'
    elif any(keyword in text for keyword in ['аграр', 'agrar', 'агро', 'agro', 'agrarbank', 'агробанк']):
        return 'Агробанк'
    elif any(keyword in text for keyword in ['миллий', 'milliy', 'milly', 'milliybank', 'миллийбанк']):
        return 'Миллий банк'
    elif any(keyword in text for keyword in ['хамкор', 'hamkor', 'xamkor', 'hamkorbank', 'хамкорбанк']):
        return 'Hamkor банк'
    elif any(keyword in text for keyword in ['микрокредит', 'mikrokredit', 'microcredit', 'микрокредитбанк']):
        return 'Микрокредитбанк'
    elif any(keyword in text for keyword in ['туран', 'turan', 'turanbank', 'туранбанк']):
        return 'Туран банк'
    elif any(keyword in text for keyword in ['брб', 'brb', 'бизнес ривож', 'biznes rivojlantirish', 'брббанк']):
        return 'БРБ банк'
    elif any(keyword in text for keyword in ['sqb', 'саноаткурилис', 'промстрой', 'узпромстройбанк', 'sqbbank']):
        return 'SQB банк'
    else:
        return 'Бошқа банк'

def get_bank_statistics():
    """Статистика по банкам из вопроса 1 с подробной детализацией"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT q1 FROM responses WHERE q1 IS NOT NULL AND q1 != ''")
    banks = cursor.fetchall()
    
    # Детальная классификация банков
    bank_names = []
    for bank in banks:
        bank_names.append(classify_bank(bank['q1']))
    
    conn.close()
    
    # Подсчитываем статистику
    bank_counter = Counter(bank_names)
    total = sum(bank_counter.values())
    
    # Сортируем по убыванию
    sorted_banks = sorted(bank_counter.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'banks': [bank[0] for bank in sorted_banks],
        'counts': [bank[1] for bank in sorted_banks],
        'total': total,
        'detailed': dict(sorted_banks)  # Детальная статистика
    }

def normalize_answer(answer):
    """Нормализация ответов для диаграмм"""
    if not answer:
        return None
    
    answer_str = str(answer).strip().lower()
    
    # Для вопросов Да/Нет
    if answer_str in ['ha', 'да', 'һа', 'yes', 'true', 'ha!']:
        return 'Ha'
    elif answer_str in ['yoq', 'нет', 'йоқ', 'no', 'false', 'yoq!']:
        return 'Yo\'q'
    elif answer_str in ['qisman', 'частично', 'жартылай', 'partially']:
        return 'Qisman'
    
    return answer.capitalize() if answer else answer

@app.route('/')
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/auth', methods=['POST'])
def auth():
    login = request.form.get('login')
    password = request.form.get('password')
    
    if login == ADMIN_CREDENTIALS['login'] and password == ADMIN_CREDENTIALS['password']:
        session['logged_in'] = True
        session['admin_language'] = 'uz'  # Язык по умолчанию
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Noto\'g\'ri login yoki parol'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/set_language/<lang>')
@login_required
def set_language(lang):
    if lang in ['uz', 'ru', 'kar']:
        session['admin_language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Общая статистика
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE completed=1")
    completed = cursor.fetchone()[0]
    
    # Статистика по банкам с детализацией
    bank_stats = get_bank_statistics()
    
    conn.close()
    
    t = get_translation()
    
    return render_template_string(DASHBOARD_TEMPLATE,
                         t=t,
                         total_users=total_users,
                         completed=completed,
                         bank_stats=bank_stats,
                         current_lang=session.get('admin_language', 'uz'),
                         zip=zip)

@app.route('/api/statistics')
@login_required
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Общая статистика
    cursor.execute("SELECT COUNT(*) FROM users")
    stats['total'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE completed=1")
    stats['completed'] = cursor.fetchone()[0]
    
    # Статистика по вопросам
    questions = ['q2', 'q3', 'q4', 'q5', 'q6', 'q8', 'q9', 'q10']
    question_stats = {}
    
    for q in questions:
        cursor.execute(f"SELECT {q}, COUNT(*) as count FROM responses WHERE {q} IS NOT NULL AND {q} != '' GROUP BY {q}")
        results = cursor.fetchall()
        
        if results:
            # Нормализуем ответы и группируем
            normalized_counts = {}
            for row in results:
                answer = row[0]
                count = row[1]
                normalized = normalize_answer(answer)
                
                if normalized:
                    if normalized in normalized_counts:
                        normalized_counts[normalized] += count
                    else:
                        normalized_counts[normalized] = count
            
            # Преобразуем в списки для диаграммы
            labels = []
            data = []
            for answer, count in normalized_counts.items():
                labels.append(answer)
                data.append(count)
            
            question_stats[q] = {
                'labels': labels,
                'data': data
            }
        else:
            # Если данных нет, создаем заглушку
            question_stats[q] = {
                'labels': ['Ma\'lumot yo\'q'],
                'data': [1]
            }
    
    conn.close()
    
    return jsonify({
        'general': stats,
        'questions': question_stats,
        'bank_stats': get_bank_statistics()
    })

@app.route('/users')
@login_required
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем список пользователей
    cursor.execute("""
    SELECT u.id, u.tg_id, u.username, u.first_name, u.last_name, u.language,
           u.started_at, u.completed, r.completed_at
    FROM users u
    LEFT JOIN responses r ON u.id = r.user_id
    ORDER BY u.started_at DESC
    """)
    
    users = cursor.fetchall()
    conn.close()
    
    t = get_translation()
    
    return render_template_string(USERS_TEMPLATE, 
                         users=users, 
                         t=t,
                         current_lang=session.get('admin_language', 'uz'))

@app.route('/user/<int:user_id>')
@login_required
def user_details(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Информация о пользователе
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    # Ответы пользователя
    cursor.execute("SELECT * FROM responses WHERE user_id=?", (user_id,))
    responses = cursor.fetchone()
    
    conn.close()
    
    t = get_translation()
    
    return render_template_string(USER_DETAILS_TEMPLATE,
                         user=user,
                         responses=responses,
                         t=t,
                         current_lang=session.get('admin_language', 'uz'))

@app.route('/user/<int:user_id>/download')
@login_required
def download_user_responses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Информация о пользователе
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    # Ответы пользователя
    cursor.execute("SELECT * FROM responses WHERE user_id=?", (user_id,))
    responses = cursor.fetchone()
    
    # Создаем текстовый файл
    output = io.StringIO()
    
    output.write(f"User ID: {user['id']}\n")
    output.write(f"Telegram ID: {user['tg_id']}\n")
    output.write(f"Username: @{user['username'] or 'N/A'}\n")
    output.write(f"Name: {user['first_name'] or ''} {user['last_name'] or ''}\n")
    output.write(f"Language: {user['language']}\n")
    output.write(f"Started: {user['started_at']}\n")
    output.write(f"Completed: {'Yes' if user['completed'] else 'No'}\n")
    output.write("-" * 50 + "\n\n")
    
    # Вопросы и ответы
    questions = [
        ("Q1: Qaysi bankda ishlaysiz?", 'q1'),
        ("Q2: Bankda korruptsiya bormi?", 'q2'),
        ("Q2 (batafsil): Korruptsiya haqida", 'q2_text'),
        ("Q3: Jamoa muhitidan qoniqasizmi?", 'q3'),
        ("Q4: Noqonuniy topshiriqlar bormi?", 'q4'),
        ("Q4 (batafsil): Noqonuniy topshiriqlar haqida", 'q4_text'),
        ("Q5: Ichki hujjatlar buzilishi bormi?", 'q5'),
        ("Q5 (batafsil): Ichki hujjatlar buzilishi haqida", 'q5_text'),
        ("Q6: Rotatsiyada manfaatlar to'qnashuvi bormi?", 'q6'),
        ("Q6 (batafsil): Rotatsiyada manfaatlar to'qnashuvi haqida", 'q6_text'),
        ("Q7: Ishga qabul tizimi (1-10)", 'q7'),
        ("Q8: Xizmat vazifalarida korruptsiya bormi?", 'q8'),
        ("Q9: Pul yig'imlari tashkil etiladimi?", 'q9'),
        ("Q9 (batafsil): Pul yig'imlari haqida", 'q9_text'),
        ("Q10: Adolatsiz qarorlar bormi?", 'q10'),
        ("Q11: Telefon raqami", 'q11'),
        ("Q12: Qo'shimcha takliflar", 'q12')
    ]
    
    for question_text, field in questions:
        answer = responses[field] if responses and responses[field] else "Javob yo'q"
        output.write(f"{question_text}\n")
        output.write(f"Javob: {answer}\n")
        output.write("-" * 30 + "\n")
    
    output.seek(0)
    
    filename = f"user_{user_id}_responses.txt"
    
    return Response(
        output.getvalue(),
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@app.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM responses WHERE user_id=?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export/index.txt')
@login_required
def export_index_txt():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT u.id, u.tg_id, u.username, u.first_name, u.last_name, u.language,
           u.started_at, u.completed, r.*
    FROM users u
    LEFT JOIN responses r ON u.id = r.user_id
    ORDER BY u.started_at DESC
    """)
    
    users = cursor.fetchall()
    
    output = io.StringIO()
    
    # Заголовки
    output.write("ID\tTelegram ID\tUsername\tFirst Name\tLast Name\tLanguage\tStarted At\tCompleted\t")
    output.write("q1\tq2\tq2_text\tq3\tq4\tq4_text\tq5\tq5_text\tq6\tq6_text\tq7\tq8\tq9\tq9_text\tq10\tq11\tq12\tCompleted At\n")
    
    # Данные
    for user in users:
        output.write(f"{user['id']}\t{user['tg_id']}\t{user['username'] or 'N/A'}\t")
        output.write(f"{user['first_name'] or 'N/A'}\t{user['last_name'] or 'N/A'}\t{user['language']}\t")
        output.write(f"{user['started_at']}\t{'Ha' if user['completed'] else 'Yoq'}\t")
        
        # Ответы
        for i in range(8, 26):  # Столбцы с ответами
            value = user[i] if user[i] is not None else ''
            output.write(f"{value}\t")
        
        output.write("\n")
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=index.txt"}
    )

@app.route('/export/bank_stats')
@login_required
def export_bank_stats():
    """Экспорт банковской статистики в Excel (CSV)"""
    bank_stats = get_bank_statistics()
    
    # Создаем CSV файл в памяти
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow(['Bank Name', 'Count', 'Percentage'])
    
    # Все 13 банков
    all_banks = [
        'Инфин банк', 'Асака банк', 'Халк банк', 'Алоқа банк', 
        'Капитал банк', 'Ипотека банк', 'Агробанк', 'Миллий банк',
        'Hamkor банк', 'Микрокредитбанк', 'Туран банк', 'БРБ банк', 'SQB банк',
        'Бошқа банк'
    ]
    
    # Данные для каждого банка
    for bank in all_banks:
        count = bank_stats['detailed'].get(bank, 0)
        percentage = (count / bank_stats['total'] * 100) if bank_stats['total'] > 0 else 0
        writer.writerow([bank, count, f"{percentage:.2f}%"])
    
    # Итоговая строка
    writer.writerow(['TOTAL', bank_stats['total'], '100%'])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=bank_statistics.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )

@app.route('/bank_users/<path:bank_name>')
@login_required
def bank_users(bank_name):
    """Белгілі бір банкта жұмыс істейтін пайдаланушыларды көрсету"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Барлық пайдаланушылар мен жауаптарды алу
    cursor.execute("""
    SELECT u.id, u.tg_id, u.username, u.first_name, u.last_name, u.language,
           u.started_at, u.completed, r.*
    FROM users u
    LEFT JOIN responses r ON u.id = r.user_id
    WHERE r.q1 IS NOT NULL AND r.q1 != ''
    """)
    
    all_users = cursor.fetchall()
    
    # Банк бойынша фильтрлеу
    filtered_users = []
    completed_count = 0
    
    for user in all_users:
        user_q1 = user['q1']
        if user_q1:
            classified_bank = classify_bank(user_q1)
            if classified_bank == unquote(bank_name):
                # Словарь құру
                user_dict = {
                    'id': user['id'],
                    'tg_id': user['tg_id'],
                    'username': user['username'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'language': user['language'],
                    'started_at': user['started_at'],
                    'completed': user['completed'],
                    'q1': user['q1'],
                    'q2': user['q2'],
                    'q2_text': user['q2_text'],
                    'q3': user['q3'],
                    'q4': user['q4'],
                    'q4_text': user['q4_text'],
                    'q5': user['q5'],
                    'q5_text': user['q5_text'],
                    'q6': user['q6'],
                    'q6_text': user['q6_text'],
                    'q7': user['q7'],
                    'q8': user['q8'],
                    'q9': user['q9'],
                    'q9_text': user['q9_text'],
                    'q10': user['q10'],
                    'q11': user['q11'],
                    'q12': user['q12']
                }
                filtered_users.append(user_dict)
                
                if user['completed']:
                    completed_count += 1
    
    conn.close()
    
    t = get_translation()
    
    return render_template_string(BANK_USERS_TEMPLATE,
                         t=t,
                         bank_name=unquote(bank_name),
                         users=filtered_users,
                         completed_count=completed_count,
                         current_lang=session.get('admin_language', 'uz'))

@app.route('/export/bank_users_excel/<path:bank_name>')
@login_required
def export_bank_users_excel(bank_name):
    """Белгілі бір банктың пайдаланушыларын Excel файлына экспорттау"""
    
    bank_name = unquote(bank_name)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Барлық пайдаланушылар мен жауаптарды алу
    cursor.execute("""
    SELECT u.id, u.tg_id, u.username, u.first_name, u.last_name, u.language,
           u.started_at, u.completed, r.*
    FROM users u
    LEFT JOIN responses r ON u.id = r.user_id
    WHERE r.q1 IS NOT NULL AND r.q1 != ''
    """)
    
    all_users = cursor.fetchall()
    
    # Банк бойынша фильтрлеу
    filtered_users = []
    
    for user in all_users:
        user_q1 = user['q1']
        if user_q1:
            classified_bank = classify_bank(user_q1)
            if classified_bank == bank_name:
                filtered_users.append(user)
    
    # CSV файлды құру
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовоктар
    headers = [
        'ID', 'Telegram ID', 'Username', 'First Name', 'Last Name', 'Language',
        'Started At', 'Completed', 'Bank (Q1)', 
        'Q2: Bankda korruptsiya bormi?', 'Q2 (batafsil)',
        'Q3: Jamoa muhitidan qoniqasizmi?',
        'Q4: Noqonuniy topshiriqlar bormi?', 'Q4 (batafsil)',
        'Q5: Ichki hujjatlar buzilishi bormi?', 'Q5 (batafsil)',
        'Q6: Rotatsiyada manfaatlar to\'qnashuvi bormi?', 'Q6 (batafsil)',
        'Q7: Ishga qabul tizimi (1-10)',
        'Q8: Xizmat vazifalarida korruptsiya bormi?',
        'Q9: Pul yig\'imlari tashkil etiladimi?', 'Q9 (batafsil)',
        'Q10: Adolatsiz qarorlar bormi?',
        'Q11: Telefon raqami',
        'Q12: Qo\'shimcha takliflar',
        'Completed At'
    ]
    
    writer.writerow(headers)
    
    # Деректерді жазу
    for user in filtered_users:
        row = [
            user['id'],
            user['tg_id'],
            user['username'] or '',
            user['first_name'] or '',
            user['last_name'] or '',
            user['language'],
            user['started_at'],
            'Ha' if user['completed'] else 'Yoq',
            user['q1'] or '',
            user['q2'] or '',
            user['q2_text'] or '',
            user['q3'] or '',
            user['q4'] or '',
            user['q4_text'] or '',
            user['q5'] or '',
            user['q5_text'] or '',
            user['q6'] or '',
            user['q6_text'] or '',
            user['q7'] or '',
            user['q8'] or '',
            user['q9'] or '',
            user['q9_text'] or '',
            user['q10'] or '',
            user['q11'] or '',
            user['q12'] or '',
            user['completed_at'] or ''
        ]
        writer.writerow(row)
    
    conn.close()
    
    # Файл аты
    safe_bank_name = "".join(x for x in bank_name if x.isalnum() or x in (' ', '-', '_')).rstrip()
    filename = f"{safe_bank_name}_users.csv"
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    t = get_translation()
    
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if old_password != ADMIN_CREDENTIALS['password']:
            flash('Eski parol noto\'g\'ri', 'error')
        elif new_password != confirm_password:
            flash('Yangi parollar mos kelmadi', 'error')
        else:
            ADMIN_CREDENTIALS['password'] = new_password
            flash('Parol muvaffaqiyatli o\'zgartirildi', 'success')
    
    return render_template_string(SETTINGS_TEMPLATE, 
                         t=t, 
                         current_lang=session.get('admin_language', 'uz'))

# Функция для создания тестовых данных
@app.route('/create_test_data')
def create_test_data():
    """Создание тестовых данных для проверки диаграмм"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем тестовых пользователей
    test_users = [
        (123456789, 'test_user1', 'Test', 'User1', 'uz', 1),
        (987654321, 'test_user2', 'Test', 'User2', 'ru', 1),
        (555555555, 'test_user3', 'Test', 'User3', 'kar', 1),
    ]
    
    for tg_id, username, first_name, last_name, language, completed in test_users:
        cursor.execute("""
        INSERT OR IGNORE INTO users (tg_id, username, first_name, last_name, language, started_at, completed)
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        """, (tg_id, username, first_name, last_name, language, completed))
        
        user_id = cursor.lastrowid
        
        # Создаем тестовые ответы для каждого пользователя
        test_responses = [
            ('Инфин банк', 'Ha', 'Qisman', 'Yoq', 'Ha', 'Yoq', '8', 'Ha', 'Yoq', 'Ha', '998901234567', 'Test javob 1'),
            ('Асака банк', 'Yoq', 'Ha', 'Ha', 'Yoq', 'Ha', '6', 'Yoq', 'Ha', 'Yoq', '998907654321', 'Test javob 2'),
            ('Халк банк', 'Ha', 'Ha', 'Yoq', 'Ha', 'Yoq', '9', 'Ha', 'Yoq', 'Ha', '998909876543', 'Test javob 3'),
            ('Алоқа банк', 'Yoq', 'Qisman', 'Ha', 'Yoq', 'Ha', '7', 'Yoq', 'Ha', 'Yoq', '998905432109', 'Test javob 4'),
            ('Капитал банк', 'Ha', 'Yoq', 'Yoq', 'Ha', 'Yoq', '8', 'Ha', 'Yoq', 'Ha', '998903456789', 'Test javob 5'),
        ]
        
        for resp in test_responses:
            cursor.execute("""
            INSERT OR REPLACE INTO responses 
            (user_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (user_id, *resp))
    
    conn.commit()
    conn.close()
    
    return "Test data created successfully!"

# Инициализация базы данных при запуске
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')