import type { Template } from '../types';

export const defaultTemplates: Template[] = [
    {
        id: 'welcome-example',
        name: 'Welcome Email Example',
        subject: 'Welcome to Our Community, {{company_name}}!',
        content: `
            <div style="font-family: Inter, system-ui, -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">Welcome to the Community, John Doe! 🎉</h1>
                </div>
                
                <div style="padding: 32px 24px; color: #1f2937;">
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                        Hi John,
                    </p>
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                        We're thrilled to have you join us! You're now part of a community that values collaboration and innovation.
                    </p>
                    
                    <div style="background: #f3f4f6; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
                        <h2 style="color: #4f46e5; font-size: 20px; margin: 0 0 16px 0;">What's Next?</h2>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            <li style="margin-bottom: 12px; display: flex; align-items: center;">
                                <span style="background: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; color: white; margin-right: 12px;">1</span>
                                <span>Complete your profile setup</span>
                            </li>
                            <li style="margin-bottom: 12px; display: flex; align-items: center;">
                                <span style="background: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; color: white; margin-right: 12px;">2</span>
                                <span>Explore our latest content</span>
                            </li>
                            <li style="display: flex; align-items: center;">
                                <span style="background: #4f46e5; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; color: white; margin-right: 12px;">3</span>
                                <span>Connect with other members</span>
                            </li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="https://www.example.com/get-started" style="display: inline-block; background: #4f46e5; color: white; padding: 12px 32px; text-decoration: none; border-radius: 6px; font-weight: 500; transition: background 0.3s ease;">Get Started →</a>
                    </div>
                </div>
                
                <div style="background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px;">
                    <p style="margin: 0 0 12px 0;">
                        You received this email because you signed up for Example Company.
                    </p>
                    <div>
                        <a href="https://www.example.com/unsubscribe" style="color: #6b7280; text-decoration: underline;">Unsubscribe</a>
                        •
                        <a href="https://www.example.com/privacy-policy" style="color: #6b7280; text-decoration: underline;">Privacy Policy</a>
                    </div>
                </div>
            </div>
        `
    },
    {
        id: 'product-update-example',
        name: 'Product Update Example',
        subject: 'Exciting New Features Just Launched!',
        content: `
            <div style="font-family: Inter, system-ui, -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">🚀 New Features Alert</h1>
                    <p style="color: #e0e7ff; margin: 12px 0 0 0; font-size: 16px;">We've made our platform even better!</p>
                </div>
                
                <div style="padding: 32px 24px; color: #1f2937;">
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                        Hi Jane,
                    </p>
                    
                    <div style="margin-bottom: 32px;">
                        <h2 style="color: #1d4ed8; font-size: 20px; margin: 0 0 20px 0;">What's New?</h2>
                        
                        <div style="background: #f3f4f6; border-radius: 8px; padding: 24px; margin-bottom: 16px;">
                            <h3 style="color: #1e40af; font-size: 18px; margin: 0 0 12px 0;">Feature 1: Enhanced Analytics</h3>
                            <p style="margin: 0; line-height: 1.6;">Get deeper insights into your audience engagement with our new analytics dashboard.</p>
                        </div>
                        
                        <div style="background: #f3f4f6; border-radius: 8px; padding: 24px; margin-bottom: 16px;">
                            <h3 style="color: #1e40af; font-size: 18px; margin: 0 0 12px 0;">Feature 2: Customizable Templates</h3>
                            <p style="margin: 0; line-height: 1.6;">Create stunning newsletters with our new customizable templates.</p>
                        </div>
                        
                        <div style="background: #f3f4f6; border-radius: 8px; padding: 24px;">
                            <h3 style="color: #1e40af; font-size: 18px; margin: 0 0 12px 0;">Feature 3: Improved User Interface</h3>
                            <p style="margin: 0; line-height: 1.6;">Enjoy a smoother experience with our redesigned user interface.</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="https://www.example.com/new-features" style="display: inline-block; background: #2563eb; color: white; padding: 12px 32px; text-decoration: none; border-radius: 6px; font-weight: 500; transition: background 0.3s ease;">Try New Features →</a>
                    </div>
                </div>
                
                <div style="background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px;">
                    <div style="margin-bottom: 12px;">
                        <a href="https://www.example.com/documentation" style="color: #2563eb; text-decoration: none; margin: 0 8px;">Documentation</a>
                        <a href="https://www.example.com/support" style="color: #2563eb; text-decoration: none; margin: 0 8px;">Support</a>
                        <a href="https://www.example.com/feedback" style="color: #2563eb; text-decoration: none; margin: 0 8px;">Give Feedback</a>
                    </div>
                    <div>
                        <a href="https://www.example.com/unsubscribe" style="color: #6b7280; text-decoration: underline;">Unsubscribe</a>
                    </div>
                </div>
            </div>
        `
    },
    {
        id: 'monthly-newsletter-example',
        name: 'Monthly Newsletter Example',
        subject: 'March Newsletter: Latest Updates & Insights',
        content: `
            <div style="font-family: Inter, system-ui, -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #059669, #047857); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">March Newsletter</h1>
                    <p style="color: #d1fae5; margin: 12px 0 0 0; font-size: 16px;">Your monthly dose of updates and insights</p>
                </div>
                
                <div style="padding: 32px 24px; color: #1f2937;">
                    <p style="font-size: 16px; line-height: 1.6; margin-bottom: 24px;">
                        Hi Sarah,<br><br>
                        Here's your monthly roundup of the latest updates, insights, and highlights from Example Company.
                    </p>
                    
                    <div style="background: linear-gradient(135deg, #047857, #059669); border-radius: 8px; padding: 24px; color: white; margin-bottom: 32px;">
                        <h2 style="margin: 0 0 16px 0; font-size: 20px;">📌 Featured Story</h2>
                        <h3 style="margin: 0 0 12px 0; font-size: 18px;">New Partnership Announcement</h3>
                        <p style="margin: 0 0 16px 0; line-height: 1.6;">We are excited to announce our new partnership with XYZ Corp, which will enhance our service offerings.</p>
                        <a href="https://www.example.com/featured-story" style="display: inline-block; background: white; color: #059669; padding: 8px 20px; text-decoration: none; border-radius: 4px; font-weight: 500;">Read More →</a>
                    </div>
                    
                    <div style="margin-bottom: 32px;">
                        <h2 style="color: #059669; font-size: 20px; margin: 0 0 20px 0;">Latest Updates</h2>
                        
                        <div style="background: #f3f4f6; border-radius: 8px; padding: 24px;">
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #065f46; font-size: 18px; margin: 0 0 8px 0;">New Feature: User Profiles</h3>
                                <p style="margin: 0 0 12px 0; line-height: 1.6;">You can now create personalized user profiles to enhance your experience.</p>
                                <a href="https://www.example.com/user-profiles" style="color: #059669; text-decoration: none; font-weight: 500;">Learn more →</a>
                            </div>
                            
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #065f46; font-size: 18px; margin: 0 0 8px 0;">Upcoming Webinar: Tips & Tricks</h3>
                                <p style="margin: 0 0 12px 0; line-height: 1.6;">Join us for a webinar on how to maximize your use of our platform.</p>
                                <a href="https://www.example.com/webinar" style="color: #059669; text-decoration: none; font-weight: 500;">Learn more →</a>
                            </div>
                            
                            <div>
                                <h3 style="color: #065f46; font-size: 18px; margin: 0 0 8px 0;">Community Spotlight: User of the Month</h3>
                                <p style="margin: 0 0 12px 0; line-height: 1.6;">Congratulations to Jane Smith for being our User of the Month!</p>
                                <a href="https://www.example.com/community-spotlight" style="color: #059669; text-decoration: none; font-weight: 500;">Learn more →</a>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #ecfdf5; border-radius: 8px; padding: 24px; margin-bottom: 32px;">
                        <h2 style="color: #059669; font-size: 20px; margin: 0 0 16px 0;">💡 Community Spotlight</h2>
                        <p style="margin: 0 0 16px 0; line-height: 1.6;">Join our community discussions and share your thoughts!</p>
                        <a href="https://www.example.com/community" style="color: #059669; text-decoration: none; font-weight: 500;">Join the discussion →</a>
                    </div>
                </div>
                
                <div style="background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px;">
                    <div style="margin-bottom: 12px;">
                        <a href="https://www.example.com/social/twitter" style="color: #059669; text-decoration: none; margin: 0 8px;">Twitter</a>
                        <a href="https://www.example.com/social/linkedin" style="color: #059669; text-decoration: none; margin: 0 8px;">LinkedIn</a>
                        <a href="https://www.example.com/social/facebook" style="color: #059669; text-decoration: none; margin: 0 8px;">Facebook</a>
                    </div>
                    <p style="margin: 12px 0;">
                        © 2023 Example Company. All rights reserved.
                    </p>
                    <div>
                        <a href="https://www.example.com/unsubscribe" style="color: #6b7280; text-decoration: underline;">Unsubscribe</a>
                        •
                        <a href="https://www.example.com/privacy-policy" style="color: #6b7280; text-decoration: underline;">Privacy Policy</a>
                    </div>
                </div>
            </div>
        `
    }
]; 