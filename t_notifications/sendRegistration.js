const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

exports.handler = async (event) => {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { email,  name, title, pickupDate, maxReturnDate } = body;

    // Get Gmail credentials from environment variables
    const gmailUser = process.env.GMAIL_USER;
    const gmailPass = process.env.GMAIL_PASS;

    // Read and populate the HTML template
    const templatePath = path.resolve(__dirname, 'sendRegistration.html'); // Ensure this matches your template file path
    let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

    // Replace placeholders in the HTML template with actual data
    htmlTemplate = htmlTemplate
        .replace('{{name}}', name)
        .replace('{{title}}', title)
        .replace('{{pickupDate}}', pickupDate)
        .replace('{{maxReturnDate}}', maxReturnDate);

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
        from: `"Bibliokuna" <${gmailUser}>`, // Sender address
        to: email,                          // Recipient address
        subject: "Confirmación de Reserva de Libro",                   // Subject of the email
        html: htmlTemplate,                 // Use HTML template as the body
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
