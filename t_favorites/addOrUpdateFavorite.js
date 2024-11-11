const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    // Obtener los parámetros de consulta y el body
    const tenant_id = event.query.tenant_id;
    const email = event.query.email;
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const isbn = body.isbn;

    // Construir la clave de partición y de ordenación
    const itemKey = `${email}#${isbn}`;

    // Actualizar el campo isFavorite a true
    await dynamo.send(
      new UpdateCommand({
        TableName: tableName,
        Key: {
          tenant_id,
          "email#isbn": itemKey,
        },
        UpdateExpression: "SET isFavorite = :val",
        ExpressionAttributeValues: {
          ":val": true,
        },
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Favorite updated successfully" }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
