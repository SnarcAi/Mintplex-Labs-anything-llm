/**
 * JSON Training Dataset Generator
 * Generates high-quality training data for fine-tuning LLMs on JSON tasks
 */

const fs = require('fs');
const path = require('path');

class TrainingDatasetGenerator {
  constructor() {
    this.tasks = this._initializeTasks();
  }

  /**
   * Generate complete training dataset in various formats
   */
  generateDataset(options = {}) {
    const {
      count = 1000,
      format = 'jsonl', // jsonl, alpaca, sharegpt
      taskTypes = ['all'],
      outputPath = './json_training_dataset.jsonl'
    } = options;

    const examples = [];
    const tasksToGenerate = taskTypes.includes('all')
      ? Object.keys(this.tasks)
      : taskTypes;

    const countPerTask = Math.floor(count / tasksToGenerate.length);

    for (const taskType of tasksToGenerate) {
      for (let i = 0; i < countPerTask; i++) {
        const example = this._generateExample(taskType);
        examples.push(example);
      }
    }

    // Shuffle examples
    this._shuffle(examples);

    // Format and save
    const formatted = this._formatDataset(examples, format);

    if (outputPath) {
      this._saveDataset(formatted, outputPath, format);
    }

    return {
      success: true,
      count: examples.length,
      format,
      examples: examples.slice(0, 5), // Return first 5 as preview
      outputPath,
      message: `Generated ${examples.length} training examples`
    };
  }

  /**
   * Generate single training example
   */
  _generateExample(taskType) {
    const generator = this.tasks[taskType];
    if (!generator) {
      throw new Error(`Unknown task type: ${taskType}`);
    }

    return generator.call(this);
  }

  /**
   * Initialize all task generators
   */
  _initializeTasks() {
    return {
      // 1. JSON Validation
      json_validation: () => {
        const validJSON = this._generateRandomJSON();
        return {
          instruction: "Validate the following JSON and check for syntax errors.",
          input: JSON.stringify(validJSON, null, 2),
          output: "The JSON is valid. No syntax errors found."
        };
      },

      json_validation_error: () => {
        const invalidJSON = this._generateInvalidJSON();
        return {
          instruction: "Validate the following JSON and identify any syntax errors.",
          input: invalidJSON,
          output: this._describeJSONErrors(invalidJSON)
        };
      },

      // 2. JSON Error Fixing
      json_fix: () => {
        const { broken, fixed, errors } = this._generateBrokenJSON();
        return {
          instruction: "Fix the syntax errors in the following JSON.",
          input: broken,
          output: `Fixed JSON:\n${JSON.stringify(fixed, null, 2)}\n\nErrors fixed: ${errors.join(', ')}`
        };
      },

      // 3. Schema Inference
      schema_inference: () => {
        const data = this._generateRandomJSON();
        const schema = this._inferSchema(data);
        return {
          instruction: "Infer a JSON Schema from the following JSON data.",
          input: JSON.stringify(data, null, 2),
          output: `Inferred JSON Schema:\n${JSON.stringify(schema, null, 2)}`
        };
      },

      // 4. Schema Validation
      schema_validation: () => {
        const schema = this._generateSchema();
        const data = this._generateDataFromSchema(schema);
        const isValid = Math.random() > 0.5;

        const testData = isValid ? data : this._corruptData(data);

        return {
          instruction: `Validate the following JSON data against this schema:\n${JSON.stringify(schema, null, 2)}`,
          input: JSON.stringify(testData, null, 2),
          output: isValid
            ? "The data is valid according to the schema."
            : "The data does NOT conform to the schema. Validation errors found."
        };
      },

      // 5. Data Generation
      data_generation: () => {
        const schema = this._generateSchema();
        const data = this._generateDataFromSchema(schema);

        return {
          instruction: `Generate JSON data that conforms to this schema:\n${JSON.stringify(schema, null, 2)}`,
          input: "Generate 1 example",
          output: JSON.stringify(data, null, 2)
        };
      },

      // 6. Data Transformation
      data_transformation: () => {
        const source = this._generateRandomJSON();
        const { transformed, description } = this._transformData(source);

        return {
          instruction: description,
          input: JSON.stringify(source, null, 2),
          output: JSON.stringify(transformed, null, 2)
        };
      },

      // 7. JSON Analysis
      json_analysis: () => {
        const data = this._generateComplexJSON();
        const analysis = this._analyzeData(data);

        return {
          instruction: "Analyze the structure and content of the following JSON.",
          input: JSON.stringify(data, null, 2),
          output: analysis
        };
      },

      // 8. JSON Comparison
      json_comparison: () => {
        const original = this._generateRandomJSON();
        const modified = this._modifyData(original);
        const differences = this._findDifferences(original, modified);

        return {
          instruction: `Compare these two JSON objects and identify the differences:\n\nJSON A:\n${JSON.stringify(original, null, 2)}\n\nJSON B:\n${JSON.stringify(modified, null, 2)}`,
          input: "",
          output: differences
        };
      },

      // 9. JSON Optimization
      json_optimization: () => {
        const bloated = this._generateBloatedJSON();
        const optimized = this._optimizeJSON(bloated);

        return {
          instruction: "Optimize the following JSON by removing redundancy and improving structure.",
          input: JSON.stringify(bloated, null, 2),
          output: `Optimized JSON:\n${JSON.stringify(optimized, null, 2)}\n\nSize reduced from ${JSON.stringify(bloated).length} to ${JSON.stringify(optimized).length} bytes.`
        };
      },

      // 10. JSONL Processing
      jsonl_processing: () => {
        const records = Array.from({ length: 5 }, () => this._generateRandomJSON());
        const jsonl = records.map(r => JSON.stringify(r)).join('\n');

        return {
          instruction: "Process the following JSONL (JSON Lines) data and provide a summary.",
          input: jsonl,
          output: `Processed ${records.length} records. Each record contains ${Object.keys(records[0]).length} fields.`
        };
      },

      // 11. Nested JSON Navigation
      json_navigation: () => {
        const data = this._generateNestedJSON();
        const path = this._randomPath(data);
        const value = this._getValueAtPath(data, path);

        return {
          instruction: `Extract the value at path "${path}" from the following JSON.`,
          input: JSON.stringify(data, null, 2),
          output: `Value at "${path}": ${JSON.stringify(value)}`
        };
      },

      // 12. JSON Merging
      json_merging: () => {
        const obj1 = this._generateRandomJSON();
        const obj2 = this._generateRandomJSON();
        const merged = { ...obj1, ...obj2 };

        return {
          instruction: `Merge these two JSON objects:\n\nObject 1:\n${JSON.stringify(obj1, null, 2)}\n\nObject 2:\n${JSON.stringify(obj2, null, 2)}`,
          input: "",
          output: `Merged JSON:\n${JSON.stringify(merged, null, 2)}`
        };
      }
    };
  }

  // ============ JSON GENERATION HELPERS ============

  _generateRandomJSON() {
    const types = ['user', 'product', 'config', 'data'];
    const type = this._randomChoice(types);

    switch (type) {
      case 'user':
        return {
          id: this._randomInt(1, 1000),
          name: this._randomName(),
          email: this._randomEmail(),
          age: this._randomInt(18, 80),
          active: this._randomBool()
        };
      case 'product':
        return {
          id: this._randomInt(1, 1000),
          title: `Product ${this._randomInt(1, 100)}`,
          price: this._randomFloat(10, 1000),
          inStock: this._randomBool(),
          tags: this._randomArray(['electronics', 'clothing', 'books'], 2)
        };
      case 'config':
        return {
          version: `${this._randomInt(1, 5)}.${this._randomInt(0, 10)}.${this._randomInt(0, 20)}`,
          enabled: this._randomBool(),
          timeout: this._randomInt(1000, 10000),
          retries: this._randomInt(1, 5)
        };
      default:
        return {
          key: this._randomString(8),
          value: this._randomInt(1, 100),
          timestamp: new Date().toISOString()
        };
    }
  }

  _generateComplexJSON() {
    return {
      users: Array.from({ length: 3 }, (_, i) => ({
        id: i + 1,
        name: this._randomName(),
        email: this._randomEmail(),
        roles: this._randomArray(['admin', 'user', 'moderator'], 2)
      })),
      settings: {
        theme: this._randomChoice(['light', 'dark']),
        notifications: {
          email: this._randomBool(),
          sms: this._randomBool(),
          push: this._randomBool()
        },
        privacy: {
          profileVisible: this._randomBool(),
          showEmail: this._randomBool()
        }
      },
      metadata: {
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    };
  }

  _generateNestedJSON(depth = 3) {
    if (depth === 0) {
      return this._randomInt(1, 100);
    }

    return {
      level: depth,
      value: this._randomInt(1, 100),
      nested: this._generateNestedJSON(depth - 1)
    };
  }

  _generateInvalidJSON() {
    const errors = [
      '{"key": "value",}', // trailing comma
      '{key: "value"}', // unquoted key
      "{'key': 'value'}", // single quotes
      '{"key": "value"', // missing closing brace
      '{"key": undefined}', // undefined value
      '{"key": "value" "key2": "value2"}', // missing comma
    ];

    return this._randomChoice(errors);
  }

  _generateBrokenJSON() {
    const fixed = this._generateRandomJSON();
    const errors = [];
    let broken = JSON.stringify(fixed, null, 2);

    // Randomly introduce errors
    const errorType = this._randomChoice(['trailing_comma', 'missing_quote', 'missing_brace']);

    switch (errorType) {
      case 'trailing_comma':
        broken = broken.replace(/\n}/g, ',\n}');
        errors.push('trailing comma');
        break;
      case 'missing_quote':
        broken = broken.replace(/"(\w+)":/g, '$1:');
        errors.push('missing quotes around keys');
        break;
      case 'missing_brace':
        broken = broken.slice(0, -1);
        errors.push('missing closing brace');
        break;
    }

    return { broken, fixed, errors };
  }

  _generateSchema() {
    return {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        email: { type: 'string', format: 'email' },
        age: { type: 'integer', minimum: 0, maximum: 120 },
        active: { type: 'boolean' }
      },
      required: ['id', 'name', 'email']
    };
  }

  _generateDataFromSchema(schema) {
    if (schema.type === 'object') {
      const obj = {};
      for (const [key, propSchema] of Object.entries(schema.properties || {})) {
        obj[key] = this._generateValueFromSchema(propSchema);
      }
      return obj;
    }
    return this._generateValueFromSchema(schema);
  }

  _generateValueFromSchema(schema) {
    switch (schema.type) {
      case 'string':
        if (schema.format === 'email') return this._randomEmail();
        return this._randomString(10);
      case 'integer':
        return this._randomInt(schema.minimum || 0, schema.maximum || 100);
      case 'number':
        return this._randomFloat(0, 100);
      case 'boolean':
        return this._randomBool();
      case 'array':
        return Array.from({ length: 3 }, () => this._generateValueFromSchema(schema.items || { type: 'string' }));
      default:
        return null;
    }
  }

  _inferSchema(data) {
    const type = Array.isArray(data) ? 'array' : typeof data;

    if (type === 'object' && data !== null) {
      return {
        type: 'object',
        properties: Object.fromEntries(
          Object.entries(data).map(([key, value]) => [key, this._inferSchema(value)])
        )
      };
    } else if (type === 'array') {
      return {
        type: 'array',
        items: data.length > 0 ? this._inferSchema(data[0]) : { type: 'string' }
      };
    } else {
      return { type: type === 'object' ? 'null' : type };
    }
  }

  _corruptData(data) {
    const corrupted = JSON.parse(JSON.stringify(data));
    const keys = Object.keys(corrupted);
    if (keys.length > 0) {
      const key = this._randomChoice(keys);
      corrupted[key] = 'INVALID_VALUE_12345';
    }
    return corrupted;
  }

  _transformData(data) {
    const transformations = [
      {
        description: "Convert all string values to uppercase",
        transform: (obj) => {
          const result = {};
          for (const [key, value] of Object.entries(obj)) {
            result[key] = typeof value === 'string' ? value.toUpperCase() : value;
          }
          return result;
        }
      },
      {
        description: "Add a timestamp field to the JSON",
        transform: (obj) => ({ ...obj, timestamp: new Date().toISOString() })
      },
      {
        description: "Rename the 'name' field to 'fullName'",
        transform: (obj) => {
          const { name, ...rest } = obj;
          return name ? { fullName: name, ...rest } : obj;
        }
      }
    ];

    const chosen = this._randomChoice(transformations);
    return {
      transformed: chosen.transform(data),
      description: chosen.description
    };
  }

  _analyzeData(data) {
    const keys = Object.keys(data);
    const depth = this._computeDepth(data);
    const size = JSON.stringify(data).length;

    return `Analysis:\n- Total keys: ${keys.length}\n- Nesting depth: ${depth}\n- Size: ${size} bytes\n- Structure: ${Array.isArray(data) ? 'array' : 'object'}`;
  }

  _modifyData(data) {
    const modified = JSON.parse(JSON.stringify(data));
    const keys = Object.keys(modified);

    if (keys.length > 0) {
      const key = this._randomChoice(keys);
      modified[key] = 'MODIFIED_VALUE';
    }

    return modified;
  }

  _findDifferences(obj1, obj2) {
    const diffs = [];

    for (const key in obj1) {
      if (JSON.stringify(obj1[key]) !== JSON.stringify(obj2[key])) {
        diffs.push(`Field '${key}' changed from ${JSON.stringify(obj1[key])} to ${JSON.stringify(obj2[key])}`);
      }
    }

    return diffs.length > 0 ? diffs.join('\n') : 'No differences found';
  }

  _generateBloatedJSON() {
    return {
      id: 1,
      id_backup: 1,
      id_copy: 1,
      name: "Test",
      name_display: "Test",
      unused_field_1: null,
      unused_field_2: null,
      data: {
        value: 100,
        value_copy: 100
      }
    };
  }

  _optimizeJSON(data) {
    // Remove duplicate and null values
    const optimized = {};

    for (const [key, value] of Object.entries(data)) {
      if (value !== null && !key.includes('backup') && !key.includes('copy') && !key.includes('unused')) {
        optimized[key] = value;
      }
    }

    return optimized;
  }

  _randomPath(data, currentPath = '') {
    const keys = Object.keys(data);
    if (keys.length === 0) return currentPath;

    const key = this._randomChoice(keys);
    const newPath = currentPath ? `${currentPath}.${key}` : key;

    if (typeof data[key] === 'object' && data[key] !== null && Math.random() > 0.5) {
      return this._randomPath(data[key], newPath);
    }

    return newPath;
  }

  _getValueAtPath(data, path) {
    const keys = path.split('.');
    let value = data;

    for (const key of keys) {
      value = value?.[key];
    }

    return value;
  }

  _computeDepth(data, current = 0) {
    if (typeof data !== 'object' || data === null) return current;

    const depths = Object.values(data).map(val => this._computeDepth(val, current + 1));
    return depths.length > 0 ? Math.max(...depths) : current;
  }

  _describeJSONErrors(invalidJSON) {
    const errors = [];

    if (invalidJSON.includes(',}') || invalidJSON.includes(',]')) {
      errors.push('Trailing comma detected');
    }
    if (invalidJSON.match(/\{[^"]*:/)) {
      errors.push('Unquoted object key detected');
    }
    if (invalidJSON.includes("'")) {
      errors.push('Single quotes used instead of double quotes');
    }

    return errors.length > 0
      ? `Syntax errors found:\n${errors.map(e => `- ${e}`).join('\n')}`
      : 'Unable to parse JSON';
  }

  // ============ FORMATTING & SAVING ============

  _formatDataset(examples, format) {
    switch (format) {
      case 'jsonl':
        return examples.map(ex => JSON.stringify(ex)).join('\n');

      case 'alpaca':
        return JSON.stringify(examples.map(ex => ({
          instruction: ex.instruction,
          input: ex.input,
          output: ex.output
        })), null, 2);

      case 'sharegpt':
        return JSON.stringify(examples.map(ex => ({
          conversations: [
            { from: 'human', value: `${ex.instruction}\n\n${ex.input}` },
            { from: 'gpt', value: ex.output }
          ]
        })), null, 2);

      default:
        return JSON.stringify(examples, null, 2);
    }
  }

  _saveDataset(data, filepath, format) {
    try {
      fs.writeFileSync(filepath, data, 'utf8');
      console.log(`Dataset saved to ${filepath}`);
    } catch (error) {
      console.error('Error saving dataset:', error);
    }
  }

  // ============ UTILITY FUNCTIONS ============

  _randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  _randomFloat(min, max) {
    return parseFloat((Math.random() * (max - min) + min).toFixed(2));
  }

  _randomBool() {
    return Math.random() > 0.5;
  }

  _randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
  }

  _randomArray(items, count) {
    return items.sort(() => Math.random() - 0.5).slice(0, count);
  }

  _randomString(length) {
    return Math.random().toString(36).substring(2, 2 + length);
  }

  _randomName() {
    const first = ['John', 'Jane', 'Bob', 'Alice', 'Charlie'];
    const last = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown'];
    return `${this._randomChoice(first)} ${this._randomChoice(last)}`;
  }

  _randomEmail() {
    return `user${this._randomInt(1, 1000)}@example.com`;
  }

  _shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }
}

module.exports = TrainingDatasetGenerator;

// CLI Usage
if (require.main === module) {
  const generator = new TrainingDatasetGenerator();

  const result = generator.generateDataset({
    count: 5000,
    format: 'jsonl',
    taskTypes: ['all'],
    outputPath: './json_training_5k.jsonl'
  });

  console.log('Training dataset generated:');
  console.log(`- Total examples: ${result.count}`);
  console.log(`- Format: ${result.format}`);
  console.log(`- Output: ${result.outputPath}`);
  console.log('\nFirst 3 examples:');
  console.log(JSON.stringify(result.examples.slice(0, 3), null, 2));
}
