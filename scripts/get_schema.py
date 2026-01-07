"""
Get the schema of image_analysis_results.json using genson
"""
from genson import SchemaBuilder
import json

# Load the image analysis results
with open('image_analysis_results.json', 'r') as f:
    data = json.load(f)

# Build the schema
builder = SchemaBuilder()
builder.add_object(data)

schema = builder.to_schema()

# Print the schema
print(json.dumps(schema, indent=2))

# Save the schema to a file
with open('image_analysis_schema.json', 'w') as f:
    json.dump(schema, f, indent=2)

print("\n✓ Schema saved to image_analysis_schema.json")
