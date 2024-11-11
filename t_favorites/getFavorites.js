const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, QueryCommand } = require("@aws-sdk/lib-dynamodb");

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);
const tableName = process.env.FAVORITES_TABLE_NAME;

exports.handler = async (event) => {
  try {
    // Obtener los parámetros de consulta
    const tenant_id = event.query.tenant_id;
    const email = event.query.email;

    // Consultar los favoritos para el usuario especificado
    const result = await dynamo.send(
      new QueryCommand({
        TableName: tableName,
        KeyConditionExpression: "tenant_id = :tenant_id AND begins_with(email#isbn, :email)",
        ExpressionAttributeValues: {
          ":tenant_id": tenant_id,
          ":email": email,
        },
      })
    );

    // Formatear la respuesta
    const favorites = result.Items.map((item) => ({
      isbn: item["email#isbn"].split("#")[1],
      isFavorite: item.isFavorite,
    }));

    return favorites;
  } catch (error) {
    return error;
  }
};
