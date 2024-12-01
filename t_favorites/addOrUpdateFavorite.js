const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, UpdateCommand, GetCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;
const MU_url = process.env.USERS_URL;

async function validateToken(token) {
  if (!token) {
    throw new Error("No se envió ningún token");
  }

  const token_data = { token };

  //Validar token
  const response = await fetch(MU_url, {
    method: 'POST',
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(token_data)
  });

  return await response.json();
}

exports.handler = async (event) => {
  try {
    // Parsear el cuerpo de la solicitud y extraer los datos
    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;
    const { isbn } = body;

    //Obtener token
    const headers = typeof event.headers === "string" ? JSON.parse(event.headers) : event.headers;
    const token = headers.Authorization;

    const response = await validateToken(token);

    if(response.statusCode === 403) {
      return {
        statusCode: 403,
        body: {
          message: "Token no válido"
        }
      };
    };

    const tenant_id = response.body.tenant_id;
    const email = response.body.email;

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
