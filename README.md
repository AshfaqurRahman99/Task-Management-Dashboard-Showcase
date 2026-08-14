# Task-Management-Dashboard-Showcase
# 🚀 Centralized Task Management & Workflow Optimization System (PYF)

A real-time, scalable task management dashboard engineered to streamline organizational operations, automate reporting, and enhance team accountability. 

## 🏗️ System Architecture
```mermaid
graph LR
    A[👤 Admin / User] -->|Task Input| B(💻 Streamlit Dashboard)
    B <-->|Read / Write| C[(📊 Google Sheets API)]
    B -->|Trigger| D{📧 SMTP Server}
    D -->|Notify| E[📫 User Inbox]
    
    style A fill:#f9f9f9,stroke:#333,stroke-width:2px
    style B fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style C fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style D fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style E fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```
### 🛡️ What's New in Version 1.2 (Security & Authentication Upgrade)
* **Cryptographic Password Hashing:** Upgraded from plaintext database storage to secure password hashing using `Werkzeug` to prevent data breaches.
* **Secure Session Management:** Replaced vulnerable plaintext cookies with encrypted JSON Web Tokens (JWT) for the auto-login feature, effectively eliminating session hijacking risks.
* **Cross-Site Scripting (XSS) Protection:** Implemented strict HTML escaping and URL validation across all user inputs and dynamic table rendering to prevent malicious script injections.
