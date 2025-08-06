# 🚀 AWS Deployment Guide - WoundCare AI

## 🎯 **AWS Deployment Options**

Your WoundCare AI static HTML application can be deployed to AWS using multiple approaches:

1. **S3 Static Website Hosting** (Simple & Fast)
2. **S3 + CloudFront** (Professional & Global)
3. **AWS Amplify** (Full-stack hosting)
4. **AWS Lightsail** (Simple VPS)

## 📋 **Option 1: S3 Static Website Hosting (Recommended)**

### **Prerequisites**
- AWS Account
- AWS CLI installed and configured
- Basic knowledge of AWS S3

### **Step 1: Install AWS CLI**
```bash
# macOS
brew install awscli

# Ubuntu/Debian
sudo apt-get install awscli

# Windows
# Download from: https://aws.amazon.com/cli/
```

### **Step 2: Configure AWS CLI**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your output format (json)
```

### **Step 3: Run Deployment Script**
```bash
# Make script executable
chmod +x aws-deploy.sh

# Run deployment
./aws-deploy.sh
```

### **Step 4: Manual AWS Console Setup**

#### **Create S3 Bucket**
1. Go to AWS S3 Console
2. Click **"Create bucket"**
3. Bucket name: `woundcare-ai-app` (must be globally unique)
4. Region: Choose closest to your users
5. Click **"Create bucket"**

#### **Configure Static Website Hosting**
1. Select your bucket
2. Go to **"Properties"** tab
3. Scroll to **"Static website hosting"**
4. Click **"Edit"**
5. Enable static website hosting
6. Index document: `index.html`
7. Error document: `index.html`
8. Click **"Save changes"**

#### **Set Bucket Policy**
1. Go to **"Permissions"** tab
2. Click **"Bucket policy"**
3. Add this policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::woundcare-ai-app/*"
        }
    ]
}
```

#### **Upload Files**
1. Go to **"Objects"** tab
2. Click **"Upload"**
3. Upload `index.html` and other files
4. Click **"Upload"**

### **Step 5: Get Your URL**
Your application will be available at:
```
http://woundcare-ai-app.s3-website-us-east-1.amazonaws.com
```

## 📋 **Option 2: S3 + CloudFront (Professional)**

### **Benefits of CloudFront**
- ✅ **HTTPS** - Secure connections
- ✅ **Global CDN** - Fast loading worldwide
- ✅ **Custom Domain** - Professional URL
- ✅ **Caching** - Better performance
- ✅ **DDoS Protection** - Security

### **Step 1: Complete S3 Setup**
Follow Option 1 steps 1-4 above.

### **Step 2: Create CloudFront Distribution**
1. Go to AWS CloudFront Console
2. Click **"Create Distribution"**
3. **Origin Domain**: Select your S3 bucket website endpoint
4. **Origin Path**: Leave empty
5. **Default Root Object**: `index.html`
6. **Viewer Protocol Policy**: Redirect HTTP to HTTPS
7. **Allowed HTTP Methods**: GET, HEAD
8. **Cache Policy**: CachingOptimized
9. Click **"Create Distribution"**

### **Step 3: Get Your Professional URL**
Your application will be available at:
```
https://d1234567890abc.cloudfront.net
```

## 📋 **Option 3: AWS Amplify (Full-Stack)**

### **Step 1: Go to AWS Amplify**
1. Visit AWS Amplify Console
2. Click **"New app"** → **"Host web app"**
3. Choose **"GitHub"** as repository source

### **Step 2: Connect Repository**
1. Select your repository: `nadia-jelani/wound`
2. Branch: `clean-branch`
3. Build settings: Leave default (no build needed)
4. Click **"Save and deploy"**

### **Step 3: Get Your URL**
Your application will be available at:
```
https://main.d1234567890abc.amplifyapp.com
```

## 📋 **Option 4: AWS Lightsail (VPS)**

### **Step 1: Create Lightsail Instance**
1. Go to AWS Lightsail Console
2. Click **"Create instance"**
3. Choose **"Linux/Unix"** platform
4. Choose **"LAMP"** blueprint
5. Choose your plan
6. Click **"Create instance"**

### **Step 2: Upload Files**
1. Connect to your instance via SSH
2. Navigate to `/opt/bitnami/apache2/htdocs/`
3. Upload your `index.html` file
4. Set proper permissions

### **Step 3: Get Your URL**
Your application will be available at your instance's public IP.

## 💰 **Cost Comparison**

| Service | Monthly Cost | Features |
|---------|-------------|----------|
| **S3 Static Website** | ~$0.50 | Basic hosting |
| **S3 + CloudFront** | ~$1-5 | HTTPS, CDN, Custom domain |
| **AWS Amplify** | Free tier | Full-stack hosting |
| **AWS Lightsail** | $3.50+ | VPS with full control |

## 🎯 **Recommended: S3 + CloudFront**

### **Why S3 + CloudFront is Best**
- ✅ **Professional** - HTTPS and custom domain
- ✅ **Fast** - Global CDN
- ✅ **Reliable** - AWS infrastructure
- ✅ **Scalable** - Handles any traffic
- ✅ **Secure** - DDoS protection
- ✅ **Cost-effective** - Pay only for usage

## 🔧 **Custom Domain Setup**

### **Step 1: Register Domain (if needed)**
1. Go to AWS Route 53 or any domain registrar
2. Register your domain (e.g., `woundcare-ai.com`)

### **Step 2: Create SSL Certificate**
1. Go to AWS Certificate Manager
2. Request certificate for your domain
3. Validate via DNS or email

### **Step 3: Update CloudFront**
1. Go to CloudFront distribution
2. Add custom domain
3. Upload SSL certificate
4. Update DNS records

## 📊 **Performance Optimization**

### **S3 Optimization**
- ✅ Enable compression
- ✅ Set proper cache headers
- ✅ Use appropriate storage class

### **CloudFront Optimization**
- ✅ Enable compression
- ✅ Set cache policies
- ✅ Configure error pages

## 🔒 **Security Best Practices**

### **S3 Security**
- ✅ Block public access (except through CloudFront)
- ✅ Use bucket policies
- ✅ Enable access logging

### **CloudFront Security**
- ✅ Use HTTPS only
- ✅ Enable security headers
- ✅ Configure WAF (optional)

## 🚀 **Deployment Commands**

### **Quick Deploy with AWS CLI**
```bash
# Create bucket
aws s3 mb s3://woundcare-ai-app

# Configure website hosting
aws s3 website s3://woundcare-ai-app --index-document index.html

# Upload files
aws s3 sync . s3://woundcare-ai-app --exclude "*.py" --exclude "*.md"

# Set bucket policy
aws s3api put-bucket-policy --bucket woundcare-ai-app --policy file://bucket-policy.json
```

### **Automated Deployment**
```bash
# Run the deployment script
./aws-deploy.sh
```

## 📱 **Testing Your Deployment**

### **Test Checklist**
- ✅ Website loads correctly
- ✅ File upload works
- ✅ Analysis results display
- ✅ Mobile responsive
- ✅ HTTPS works (if using CloudFront)
- ✅ Performance is good

## 🎯 **Perfect for LinkedIn**

### **Professional LinkedIn Post**
```
🏥 Excited to share my latest AI project: WoundCare AI - Professional Medical Analysis System!

🩹 Clinical-grade web application featuring:
• AI-powered wound detection and analysis
• Professional medical interface design
• Real-time image processing and assessment
• Medical-grade results with clinical terminology

🌐 Try it live: [YOUR_AWS_URL_HERE]

💡 Upload any wound image and receive:
✅ Professional clinical assessment
✅ Precise wound measurements (mm²)
✅ Severity classification (Mild/Moderate/Severe)
✅ Healing prognosis evaluation
✅ Medical-grade analysis reports

🔬 Built with advanced AI/ML technologies for healthcare applications.
🚀 Deployed on AWS with global CDN for optimal performance.

#AI #Healthcare #MedicalAI #ComputerVision #AWS #CloudComputing #HealthcareInnovation

⚠️ For educational and research purposes only. Always consult healthcare professionals for medical decisions.
```

## 📞 **Support**

### **AWS Documentation**
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Getting Started](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html)
- [AWS Amplify](https://docs.amplify.aws/)

### **Troubleshooting**
1. Check AWS CLI configuration
2. Verify bucket permissions
3. Test CloudFront distribution
4. Check DNS settings (if using custom domain)

---

**Your professional medical application will be live on AWS with enterprise-grade infrastructure!** 🚀