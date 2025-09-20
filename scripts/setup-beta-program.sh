#!/bin/bash

# ANZX AI Platform - Beta Program Setup
# Project: extreme-gecko-466211-t1

set -e

PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log "Setting up ANZX AI Platform Beta Program..."
log "Project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
log "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com

# Create staging environment
log "Creating staging environment..."

# Deploy staging API service
gcloud run deploy anzx-ai-core-api-staging \
    --image=australia-southeast1-docker.pkg.dev/$PROJECT_ID/anzx-ai-platform-docker/core-api:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8000 \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="ENVIRONMENT=staging,PROJECT_ID=$PROJECT_ID" \
    --set-secrets="DATABASE_URL=anzx-ai-platform-db-url:latest" \
    --tag=staging \
    --no-traffic

success "Staging environment created"

# Create beta user management system
log "Creating beta user management..."# Cr
eate Firestore database for beta user tracking
if ! gcloud firestore databases describe --database="(default)" >/dev/null 2>&1; then
    gcloud firestore databases create --region=$REGION --database="(default)"
    success "Firestore database created"
else
    warning "Firestore database already exists"
fi

# Create beta signup Cloud Function
mkdir -p /tmp/beta-signup
cat > /tmp/beta-signup/main.py << 'EOF'
import os
import json
from datetime import datetime
from google.cloud import firestore
from google.cloud import secretmanager
import functions_framework
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@functions_framework.http
def beta_signup(request):
    """Handle beta program signup"""
    
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return ({'error': 'Invalid JSON'}, 400, headers)
        
        # Validate required fields
        required_fields = ['email', 'name', 'company', 'use_case']
        for field in required_fields:
            if field not in request_json:
                return ({'error': f'Missing field: {field}'}, 400, headers)
        
        # Initialize Firestore
        db = firestore.Client()
        
        # Check if user already signed up
        existing_user = db.collection('beta_users').where('email', '==', request_json['email']).get()
        if existing_user:
            return ({'message': 'Already signed up for beta'}, 200, headers)
        
        # Create beta user record
        user_data = {
            'email': request_json['email'],
            'name': request_json['name'],
            'company': request_json['company'],
            'use_case': request_json['use_case'],
            'signup_date': datetime.now(),
            'status': 'pending',
            'priority_score': calculate_priority_score(request_json)
        }
        
        # Add to Firestore
        doc_ref = db.collection('beta_users').add(user_data)
        
        # Send confirmation email
        send_confirmation_email(request_json['email'], request_json['name'])
        
        return ({
            'message': 'Successfully signed up for beta program',
            'user_id': doc_ref[1].id
        }, 200, headers)
        
    except Exception as e:
        return ({'error': str(e)}, 500, headers)

def calculate_priority_score(user_data):
    """Calculate priority score for beta access"""
    score = 0
    
    # Company size indicators
    company = user_data.get('company', '').lower()
    if any(word in company for word in ['enterprise', 'corporation', 'group']):
        score += 30
    elif any(word in company for word in ['startup', 'pty', 'ltd']):
        score += 20
    else:
        score += 10
    
    # Use case complexity
    use_case = user_data.get('use_case', '').lower()
    if any(word in use_case for word in ['integration', 'api', 'custom', 'enterprise']):
        score += 25
    elif any(word in use_case for word in ['support', 'customer service']):
        score += 20
    else:
        score += 15
    
    # Email domain scoring
    email = user_data.get('email', '')
    if email.endswith('.com.au') or email.endswith('.au'):
        score += 15  # Australian businesses
    
    return score

def send_confirmation_email(email, name):
    """Send beta signup confirmation email"""
    # This would integrate with your email service
    # For now, just log the action
    print(f"Sending confirmation email to {email} ({name})")
EOF

cat > /tmp/beta-signup/requirements.txt << EOF
google-cloud-firestore==2.13.1
google-cloud-secret-manager==2.17.0
functions-framework==3.4.0
EOF

# Deploy beta signup function
gcloud functions deploy beta-signup \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=/tmp/beta-signup \
    --entry-point=beta_signup \
    --trigger-http \
    --allow-unauthenticated \
    --memory=256MB \
    --timeout=60s \
    --quiet

success "Beta signup function deployed"

# Create feedback collection system
mkdir -p /tmp/feedback-system
cat > /tmp/feedback-system/main.py << 'EOF'
import os
import json
from datetime import datetime
from google.cloud import firestore
import functions_framework

@functions_framework.http
def collect_feedback(request):
    """Collect user feedback"""
    
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return ({'error': 'Invalid JSON'}, 400, headers)
        
        # Initialize Firestore
        db = firestore.Client()
        
        # Create feedback record
        feedback_data = {
            'user_id': request_json.get('user_id'),
            'email': request_json.get('email'),
            'feedback_type': request_json.get('type', 'general'),
            'rating': request_json.get('rating'),
            'message': request_json.get('message'),
            'feature': request_json.get('feature'),
            'timestamp': datetime.now(),
            'status': 'new'
        }
        
        # Add to Firestore
        doc_ref = db.collection('feedback').add(feedback_data)
        
        # Trigger alert for critical feedback
        if feedback_data.get('rating') and int(feedback_data['rating']) <= 2:
            # Send alert to team
            print(f"CRITICAL FEEDBACK: {feedback_data['message']}")
        
        return ({
            'message': 'Feedback submitted successfully',
            'feedback_id': doc_ref[1].id
        }, 200, headers)
        
    except Exception as e:
        return ({'error': str(e)}, 500, headers)
EOF

cat > /tmp/feedback-system/requirements.txt << EOF
google-cloud-firestore==2.13.1
functions-framework==3.4.0
EOF

# Deploy feedback function
gcloud functions deploy feedback-collection \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=/tmp/feedback-system \
    --entry-point=collect_feedback \
    --trigger-http \
    --allow-unauthenticated \
    --memory=256MB \
    --timeout=30s \
    --quiet

success "Feedback collection function deployed"

# Create beta dashboard
mkdir -p /tmp/beta-dashboard
cat > /tmp/beta-dashboard/main.py << 'EOF'
import os
import json
from datetime import datetime, timedelta
from google.cloud import firestore
import functions_framework

@functions_framework.http
def beta_dashboard(request):
    """Beta program dashboard"""
    
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Initialize Firestore
        db = firestore.Client()
        
        # Get beta user stats
        beta_users = db.collection('beta_users').get()
        total_signups = len(beta_users)
        
        # Count by status
        status_counts = {}
        for user in beta_users:
            status = user.to_dict().get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get recent feedback
        recent_feedback = db.collection('feedback').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).get()
        
        feedback_summary = []
        for feedback in recent_feedback:
            data = feedback.to_dict()
            feedback_summary.append({
                'type': data.get('feedback_type'),
                'rating': data.get('rating'),
                'message': data.get('message', '')[:100] + '...' if len(data.get('message', '')) > 100 else data.get('message', ''),
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None
            })
        
        # Calculate average rating
        all_feedback = db.collection('feedback').where('rating', '>', 0).get()
        ratings = [int(f.to_dict().get('rating', 0)) for f in all_feedback if f.to_dict().get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        dashboard_data = {
            'beta_program': {
                'total_signups': total_signups,
                'status_breakdown': status_counts,
                'target_users': 20
            },
            'feedback': {
                'average_rating': round(avg_rating, 2),
                'total_feedback': len(all_feedback),
                'recent_feedback': feedback_summary
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return (dashboard_data, 200, headers)
        
    except Exception as e:
        return ({'error': str(e)}, 500, headers)
EOF

cat > /tmp/beta-dashboard/requirements.txt << EOF
google-cloud-firestore==2.13.1
functions-framework==3.4.0
EOF

# Deploy dashboard function
gcloud functions deploy beta-dashboard \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=/tmp/beta-dashboard \
    --entry-point=beta_dashboard \
    --trigger-http \
    --allow-unauthenticated \
    --memory=256MB \
    --timeout=30s \
    --quiet

success "Beta dashboard function deployed"

# Clean up temp files
rm -rf /tmp/beta-signup /tmp/feedback-system /tmp/beta-dashboard

# Create beta program landing page
log "Creating beta program landing page..."

mkdir -p website/beta
cat > website/beta/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Join the ANZX AI Platform Beta - Early Access Program</title>
    <meta name="description" content="Get early access to ANZX AI Platform. Join our beta program and help shape the future of AI-powered customer service.">
    <link rel="stylesheet" href="../styles/main.css">
    <link rel="stylesheet" href="styles/beta.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <img src="../images/logo.svg" alt="ANZX AI Platform" class="logo">
                <span class="logo-text">ANZX AI</span>
            </div>
            <div class="nav-menu">
                <a href="../index.html" class="nav-link">Home</a>
                <a href="../index.html#features" class="nav-link">Features</a>
                <a href="../index.html#pricing" class="nav-link">Pricing</a>
                <a href="../docs" class="nav-link">Documentation</a>
                <a href="/auth/login" class="nav-link nav-login">Login</a>
            </div>
        </div>
    </nav>

    <section class="beta-hero">
        <div class="container">
            <div class="beta-content">
                <div class="beta-badge">🚀 Beta Program</div>
                <h1 class="beta-title">Get Early Access to ANZX AI Platform</h1>
                <p class="beta-description">
                    Join our exclusive beta program and be among the first to experience the future of 
                    AI-powered customer service. Help us build something amazing while getting free access 
                    to all premium features.
                </p>
                
                <div class="beta-benefits">
                    <div class="benefit-item">
                        <span class="benefit-icon">🆓</span>
                        <span>Free Premium Access</span>
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">🎯</span>
                        <span>Direct Input on Features</span>
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">🏆</span>
                        <span>Priority Support</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section class="beta-signup">
        <div class="container">
            <div class="signup-content">
                <div class="signup-info">
                    <h2>Why Join Our Beta?</h2>
                    <ul class="beta-features">
                        <li>✅ Free access to all premium features</li>
                        <li>✅ Direct line to our development team</li>
                        <li>✅ Shape the product roadmap</li>
                        <li>✅ Exclusive beta user community</li>
                        <li>✅ Early access to new features</li>
                        <li>✅ Dedicated support channel</li>
                    </ul>
                    
                    <div class="beta-stats">
                        <div class="stat">
                            <div class="stat-number" id="beta-signups">0</div>
                            <div class="stat-label">Beta Users</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">20</div>
                            <div class="stat-label">Target Users</div>
                        </div>
                    </div>
                </div>
                
                <form class="beta-form" id="beta-signup-form">
                    <h3>Join the Beta Program</h3>
                    
                    <div class="form-group">
                        <label for="name">Full Name *</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email Address *</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="company">Company Name *</label>
                        <input type="text" id="company" name="company" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="use_case">How do you plan to use ANZX AI? *</label>
                        <textarea id="use_case" name="use_case" rows="3" required 
                                  placeholder="e.g., Customer support for e-commerce, Technical support for SaaS, Sales assistance..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="company_size">Company Size</label>
                        <select id="company_size" name="company_size">
                            <option value="">Select size</option>
                            <option value="1-10">1-10 employees</option>
                            <option value="11-50">11-50 employees</option>
                            <option value="51-200">51-200 employees</option>
                            <option value="201-1000">201-1000 employees</option>
                            <option value="1000+">1000+ employees</option>
                        </select>
                    </div>
                    
                    <div class="form-group checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="newsletter" name="newsletter" checked>
                            <span class="checkmark"></span>
                            Subscribe to product updates and beta news
                        </label>
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-large">
                        Join Beta Program
                    </button>
                    
                    <p class="form-note">
                        * Required fields. We'll review your application and get back to you within 48 hours.
                    </p>
                </form>
            </div>
        </div>
    </section>

    <section class="beta-timeline">
        <div class="container">
            <h2>Beta Program Timeline</h2>
            <div class="timeline">
                <div class="timeline-item active">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <h3>Phase 1: Core Features</h3>
                        <p>Basic AI assistants, chat widget, and knowledge base integration</p>
                        <span class="timeline-date">Now - February 2024</span>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <h3>Phase 2: Advanced Features</h3>
                        <p>Multi-channel support, advanced analytics, and custom integrations</p>
                        <span class="timeline-date">March - April 2024</span>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <h3>Phase 3: Enterprise Features</h3>
                        <p>SSO, advanced security, custom deployments, and enterprise tools</p>
                        <span class="timeline-date">May - June 2024</span>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <h3>Public Launch</h3>
                        <p>Full public availability with all features and pricing plans</p>
                        <span class="timeline-date">July 2024</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <div class="footer-logo">
                        <img src="../images/logo.svg" alt="ANZX AI Platform" class="logo">
                        <span class="logo-text">ANZX AI</span>
                    </div>
                    <p class="footer-description">
                        Intelligent virtual agents for Australian businesses.
                    </p>
                </div>
                <div class="footer-section">
                    <h4 class="footer-title">Contact</h4>
                    <ul class="footer-links">
                        <li><a href="mailto:beta@anzx-ai.com">beta@anzx-ai.com</a></li>
                        <li><a href="../index.html#contact">Contact Us</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 ANZX AI Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="scripts/beta.js"></script>
</body>
</html>
EOF

success "Beta program landing page created"

# Get function URLs
BETA_SIGNUP_URL=$(gcloud functions describe beta-signup --region=$REGION --format="value(serviceConfig.uri)")
FEEDBACK_URL=$(gcloud functions describe feedback-collection --region=$REGION --format="value(serviceConfig.uri)")
DASHBOARD_URL=$(gcloud functions describe beta-dashboard --region=$REGION --format="value(serviceConfig.uri)")

# Display summary
log "Beta program setup completed!"
echo ""
echo "📋 Beta Program Components:"
echo "=========================="
echo "✅ Staging environment deployed"
echo "✅ Beta user signup system created"
echo "✅ Feedback collection system deployed"
echo "✅ Beta dashboard created"
echo "✅ Beta landing page created"
echo ""
echo "🔗 Function URLs:"
echo "   Beta Signup: $BETA_SIGNUP_URL"
echo "   Feedback Collection: $FEEDBACK_URL"
echo "   Beta Dashboard: $DASHBOARD_URL"
echo ""
echo "🎯 Beta Program Goals:"
echo "   - Target: 10-20 pilot customers"
echo "   - Duration: 3-4 months"
echo "   - Focus: Core features and user feedback"
echo ""
echo "📊 Success Metrics:"
echo "   - User engagement and retention"
echo "   - Feature usage analytics"
echo "   - Customer satisfaction scores"
echo "   - Bug reports and resolution time"
echo ""
echo "📖 Next Steps:"
echo "   1. Review beta landing page at website/beta/index.html"
echo "   2. Set up monitoring for beta metrics"
echo "   3. Create beta user communication plan"
echo "   4. Schedule regular feedback review sessions"
echo ""

success "🎉 Beta program is ready to launch!"