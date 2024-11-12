const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    // Parsear el cuerpo de la solicitud y extraer los datos
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { tenant_id, email, isbn } = body;

    // Construir la clave de partición y de ordenación
    const itemKey = `${email}#${isbn}`;

    // Obtener el valor actual de isFavorite
    const currentItem = await dynamo.send(
      new GetCommand({
        TableName: tableName,
        Key: {
          tenant_id,
          "email#isbn": itemKey,
        },
      })
    );

    // Determinar el nuevo valor para isFavorite
    const newIsFavorite = currentItem.Item && currentItem.Item.isFavorite ? !currentItem.Item.isFavorite : true;

    // Actualizar el campo isFavorite con el nuevo valor
    await dynamo.send(
      new UpdateCommand({
        TableName: tableName,
        Key: {
          tenant_id,
          "email#isbn": itemKey,
        },
        UpdateExpression: "SET isFavorite = :val",
        ExpressionAttributeValues: {
          ":val": newIsFavorite,
        },
      })
    );

    return {
      statusCode: 200,
      body: {
        message: "Favorite updated successfully",
        isbn: body.isbn,
        isFavorite: newIsFavorite,
      }
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while updating the favorite status"
      }
    };
  }
};
