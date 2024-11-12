const nodemailer = require('nodemailer');
const AWS = require('aws-sdk');

// Configure DynamoDB client
const dynamoDB = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const { email, subject, message } = event;

    // Gmail SMTP configuration
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: 'bibliokuna@gmail.com', // Your Gmail address
            pass: 'hwzj ppwn tutm ojth', // App password
        },
    });

    // Email options
    const mailOptions = {
        from: 'bibliokuna@gmail.com', // Sender address
        to: email,                    // Recipient address
        subject: subject,             // Subject of the email
        text: message,                // Plain text body
    };

    try {
        // Send the email
        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent:', info.response);

        // Prepare data for DynamoDB
        const notificationData = {
            TableName: 't_notifications', // Replace with your table name
            Item: {
                tenant_id: 'tenant_123',   // Replace with the actual tenant_id
                type: 'reservation',      // Replace with the notification type
                notification_id: Date.now().toString(), // Unique ID (use timestamp or UUID)
                email: email,
                message: message,
                subject: subject,
                creation_time: new Date().toISOString(),
                status: 'sent',
            },
        };

        // Insert data into DynamoDB
        await dynamoDB.put(notificationData).promise();
        console.log('Notification data inserted into DynamoDB:', notificationData.Item);

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Email sent and notification logged successfully!',
                emailInfo: info.response,
            }),
        };
    } catch (error) {
        console.error('Error:', error);

        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'Failed to process email or insert into DynamoDB',
                error,
            }),
        };
    }
};
