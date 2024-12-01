const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

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

    // Consulta solo los elementos favoritos que tienen `isFavorite` como `true`
    const result = await dynamo.send(
      new QueryCommand({
        TableName: tableName,
        KeyConditionExpression: "tenant_id = :tenant_id AND begins_with(#emailIsbn, :email)",
        FilterExpression: "isFavorite = :trueVal",
        ExpressionAttributeNames: {
          "#emailIsbn": "email#isbn"
        },
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":email": email,
          ":trueVal": true
        },
      })
    );

    // Formatear solo los items con `isFavorite: true`
    const actualFavorites = result.Items.map((item) => ({
      isbn: item["email#isbn"].split("#")[1],
      isFavorite: item.isFavorite,
    }));

    return {
      statusCode: 200,
      body: actualFavorites,
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: {
        error: error.message || "An error occurred while retrieving favorite items",
      },
    };
  }
};
