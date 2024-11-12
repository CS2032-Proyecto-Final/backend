const nodemailer = require('nodemailer');

exports.handler = async () => {
    // const { email, subject, message } = event;

    // Get Gmail credentials from environment variables
    const gmailUser = process.env.GMAIL_USER;
    const gmailPass = process.env.GMAIL_PASS;

    // Gmail SMTP configuration
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: gmailUser, // Gmail address from environment variable
            pass: gmailPass, // App password from environment variable
        },
    });

    // Email options
    const mailOptions = {
        from: gmailUser, // Use the same Gmail address as the sender
        to: gmailUser,        // Recipient address
        subject: "This is a test email", // Subject of the email
        text: "Test email from me to me",    // Plain text body
    };

    try {
        // Send email
        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent:', info.response);
        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Email sent successfully!' }),
        };
    } catch (error) {
        console.error('Error sending email:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Failed to send email', error }),
        };
    }
};
