const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
const AWS = require('aws-sdk');

// Configure DynamoDB
const dynamoDb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { email, firstname, lastname, creationDate, full_name, color } = body;

    // Get Gmail credentials from environment variables
    const gmailUser = process.env.GMAIL_USER;
    const gmailPass = process.env.GMAIL_PASS;

    // Read and populate the HTML template
    const templatePath = path.resolve(__dirname, 'sendSignUp.html'); // Ensure this matches your template file path
    let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

    // Replace placeholders in the HTML template with actual data
    htmlTemplate = htmlTemplate
        .replace('{{firstname}}', firstname)
        .replace('{{lastname}}', lastname)
        .replace('{{email}}', email)
        .replace('{{creationDate}}', creationDate)
        .replace('{{full_name}}', full_name)
        .replace('{{color}}', color);

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
        subject: "Confirmación de Registro en Bibliokuna", // Subject of the email
        html: htmlTemplate,                 // Use HTML template as the body
    };

    try {
        // Send email
        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent:', info.response);

        // Insert the notification into DynamoDB
        const params = {
            TableName: "EmailsTable", // DynamoDB table name
            Item: {
                tenant_id: "Bibliokuna",        // Static tenant_id, or replace with dynamic data
                email: email,                  // Use recipient's email as the sort key
                firstname: firstname,
                lastname: lastname,
                creationDate: creationDate,
                full_name: full_name,
                color: color,
                sentAt: new Date().toISOString(), // Timestamp for the email sent
            },
        };

        await dynamoDb.put(params).promise();
        console.log('Notification saved to DynamoDB');

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Signup email sent and logged successfully!' }),
        };
    } catch (error) {
        console.error('Error sending signup email or logging notification:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Failed to send signup email or log notification', error }),
        };
    }
};
