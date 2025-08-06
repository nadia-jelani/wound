#!/bin/bash

# 🚀 AWS Deployment Script for WoundCare AI
# This script deploys your static HTML application to AWS S3 + CloudFront

echo "🩹 Deploying WoundCare AI to AWS..."

# Configuration
BUCKET_NAME="woundcare-ai-app"
REGION="us-east-1"
DISTRIBUTION_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 AWS Deployment Configuration:${NC}"
echo "   Bucket Name: $BUCKET_NAME"
echo "   Region: $REGION"
echo ""

# Step 1: Create S3 bucket
echo -e "${YELLOW}📦 Step 1: Creating S3 bucket...${NC}"
aws s3 mb s3://$BUCKET_NAME --region $REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ S3 bucket created successfully!${NC}"
else
    echo -e "${RED}❌ Failed to create S3 bucket. It might already exist.${NC}"
fi

# Step 2: Configure bucket for static website hosting
echo -e "${YELLOW}🌐 Step 2: Configuring static website hosting...${NC}"
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document index.html

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Static website hosting configured!${NC}"
else
    echo -e "${RED}❌ Failed to configure static website hosting.${NC}"
    exit 1
fi

# Step 3: Set bucket policy for public read access
echo -e "${YELLOW}🔓 Step 3: Setting bucket policy for public access...${NC}"
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bucket policy set successfully!${NC}"
else
    echo -e "${RED}❌ Failed to set bucket policy.${NC}"
    exit 1
fi

# Step 4: Upload files to S3
echo -e "${YELLOW}📤 Step 4: Uploading files to S3...${NC}"
aws s3 sync . s3://$BUCKET_NAME --exclude "*.py" --exclude "*.txt" --exclude "*.md" --exclude ".git/*" --exclude "aws-deploy.sh" --exclude "bucket-policy.json"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Files uploaded successfully!${NC}"
else
    echo -e "${RED}❌ Failed to upload files.${NC}"
    exit 1
fi

# Step 5: Create CloudFront distribution (optional)
echo -e "${YELLOW}☁️ Step 5: Creating CloudFront distribution...${NC}"
echo "This step requires manual configuration in AWS Console."
echo ""

# Get the website endpoint
WEBSITE_ENDPOINT=$(aws s3api get-bucket-website --bucket $BUCKET_NAME --query 'WebsiteConfiguration.IndexDocument.Suffix' --output text)

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Your application is now available at:${NC}"
echo "   S3 Website: http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "   S3 Website: http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
echo ""
echo -e "${BLUE}🔧 Next steps:${NC}"
echo "   1. Set up CloudFront for HTTPS and global CDN"
echo "   2. Configure custom domain (optional)"
echo "   3. Test your application"
echo ""
echo -e "${BLUE}📚 CloudFront Setup Guide:${NC}"
echo "   1. Go to AWS CloudFront Console"
echo "   2. Create Distribution"
echo "   3. Origin Domain: $BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo "   4. Origin Path: /"
echo "   5. Default Root Object: index.html"
echo "   6. Enable HTTPS"
echo ""

# Clean up temporary files
rm -f bucket-policy.json

echo -e "${GREEN}✅ AWS deployment script completed!${NC}"