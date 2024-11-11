const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    // Parsear el cuerpo de la solicitud y extraer los datos
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, email, isbn, isFavorite } = body;

    // Construir la clave de partición y de ordenación
    const itemKey = `${email}#${isbn}`;

    // Actualizar el campo isFavorite con el valor recibido en el body
    await dynamo.send(
      new UpdateCommand({
        TableName: tableName,
        Key: {
          tenant_id,
          "email_isbn": itemKey,
        },
        UpdateExpression: "SET isFavorite = :val",
        ExpressionAttributeValues: {
          ":val": isFavorite, // Se actualiza con el valor enviado en el body
        },
      })
    );

    return {
      statusCode: 200,
      message: "Favorite updated successfully" 
    };
  } catch (error) {
    return error;
  }
};
