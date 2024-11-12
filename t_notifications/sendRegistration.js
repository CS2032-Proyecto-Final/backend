const nodemailer = require('nodemailer');

exports.handler = async (event) => {
    const { email, subject, message } = event;

    // // Get Gmail credentials from environment variables
    // const gmailUser = process.env.GMAIL_USER;
    // const gmailPass = process.env.GMAIL_PASS;

    // Gmail SMTP configuration
    const transporter = nodemailer.createTransport({
        host: "smtp.gmail.com",
        port: 587,
        secure: false,
        service: 'gmail',
        auth: {
            user: "bibliokuna@gmail.com", // Gmail address from environment variable
            pass: "hwzj ppwn tutm ojth", // App password from environment variable
        },
    });

    // Email options
    const mailOptions = {
        from: "bibliokuna@gmail.com", // Use the same Gmail address as the sender
        to: email,        // Recipient address
        subject: subject, // Subject of the email
        text: message,    // Plain text body
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
