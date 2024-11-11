exports.handler = async (event) => {
  try {
    const libraryData = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    await dynamo.send(
      new PutCommand({
        TableName: tableName,
        Item: {
          tenant_id: libraryData.tenant_id,
          email_suffix: libraryData.email_suffix,
          reserv_book_time: libraryData.reserv_book_time,
          reserv_env_time: libraryData.reserv_env_time,
          color: libraryData.color,
          photo_url: libraryData.photo_url,
          env_types: libraryData.env_types,
          full_name: libraryData.full_name
        },
      })
    );

    return {
      statusCode: 200,
      body: "Library created successfully",
    };
  } catch (error) {
    return error;
  }
};
