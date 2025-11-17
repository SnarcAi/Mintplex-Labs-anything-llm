/**
 * JSON AI Processor - Advanced Offline JSON Assistant
 * Features:
 * - JSON/JSONL validation and analysis
 * - Intelligent error detection and auto-fix
 * - Schema inference and validation
 * - Smart data generation (1000+ records)
 * - Pattern recognition and transformation
 */

const Ajv = require('ajv');
const addFormats = require('ajv-formats');

class JSONAIProcessor {
  constructor() {
    this.ajv = new Ajv({ allErrors: true, verbose: true });
    addFormats(this.ajv);
  }

  /**
   * Validate JSON against schema or check syntax
   */
  validateJSON(jsonInput, schema = null) {
    try {
      const data = typeof jsonInput === 'string' ? JSON.parse(jsonInput) : jsonInput;

      if (schema) {
        const validate = this.ajv.compile(schema);
        const valid = validate(data);

        return {
          valid,
          errors: validate.errors || [],
          data,
          message: valid ? 'JSON is valid!' : 'Validation errors found'
        };
      }

      return {
        valid: true,
        data,
        message: 'JSON syntax is valid',
        structure: this._analyzeStructure(data)
      };
    } catch (error) {
      return {
        valid: false,
        error: error.message,
        syntaxError: true,
        suggestion: this._suggestFix(jsonInput, error)
      };
    }
  }

  /**
   * Automatically fix common JSON errors
   */
  fixJSON(jsonInput) {
    let fixed = jsonInput;
    const fixes = [];

    try {
      // Try direct parse first
      JSON.parse(fixed);
      return {
        success: true,
        fixed,
        original: jsonInput,
        fixes: ['No fixes needed - JSON is valid']
      };
    } catch (error) {
      // Apply common fixes

      // 1. Fix trailing commas
      if (fixed.match(/,(\s*[}\]])/g)) {
        fixed = fixed.replace(/,(\s*[}\]])/g, '$1');
        fixes.push('Removed trailing commas');
      }

      // 2. Fix missing quotes around keys
      fixed = fixed.replace(/(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g, '$1"$2":');
      if (fixed !== jsonInput) {
        fixes.push('Added quotes around object keys');
      }

      // 3. Fix single quotes to double quotes
      if (fixed.includes("'")) {
        fixed = fixed.replace(/'/g, '"');
        fixes.push('Converted single quotes to double quotes');
      }

      // 4. Fix unescaped quotes
      fixed = fixed.replace(/([^\\])"(?=(?:[^"]|"[^"]*")*"[^"]*$)/g, '$1\\"');

      // 5. Remove comments (not valid in JSON)
      fixed = fixed.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*/g, '');
      if (fixed.length !== jsonInput.length) {
        fixes.push('Removed comments');
      }

      // 6. Fix missing closing brackets/braces
      const openBraces = (fixed.match(/\{/g) || []).length;
      const closeBraces = (fixed.match(/\}/g) || []).length;
      const openBrackets = (fixed.match(/\[/g) || []).length;
      const closeBrackets = (fixed.match(/\]/g) || []).length;

      if (openBraces > closeBraces) {
        fixed += '}'.repeat(openBraces - closeBraces);
        fixes.push(`Added ${openBraces - closeBraces} closing brace(s)`);
      }
      if (openBrackets > closeBrackets) {
        fixed += ']'.repeat(openBrackets - closeBrackets);
        fixes.push(`Added ${openBrackets - closeBrackets} closing bracket(s)`);
      }

      // Try parsing again
      try {
        const parsed = JSON.parse(fixed);
        return {
          success: true,
          fixed,
          original: jsonInput,
          fixes,
          data: parsed,
          message: `Successfully fixed ${fixes.length} issue(s)`
        };
      } catch (finalError) {
        return {
          success: false,
          fixed,
          original: jsonInput,
          fixes,
          error: finalError.message,
          message: 'Could not automatically fix all errors. Manual intervention may be needed.'
        };
      }
    }
  }

  /**
   * Analyze JSON structure and provide insights
   */
  analyzeJSON(jsonInput) {
    try {
      const data = typeof jsonInput === 'string' ? JSON.parse(jsonInput) : jsonInput;

      const analysis = {
        type: Array.isArray(data) ? 'array' : typeof data,
        structure: this._analyzeStructure(data),
        statistics: this._computeStatistics(data),
        schema: this.inferSchema(data),
        recommendations: this._generateRecommendations(data)
      };

      return {
        success: true,
        analysis,
        message: 'Analysis complete'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Infer JSON schema from data
   */
  inferSchema(data, name = 'root') {
    const type = Array.isArray(data) ? 'array' : typeof data;

    if (type === 'array') {
      if (data.length === 0) {
        return { type: 'array', items: {} };
      }

      // Infer from first few items
      const samples = data.slice(0, Math.min(10, data.length));
      const itemSchemas = samples.map(item => this.inferSchema(item));

      // Merge schemas
      const mergedSchema = this._mergeSchemas(itemSchemas);

      return {
        type: 'array',
        items: mergedSchema,
        minItems: data.length,
        maxItems: data.length
      };
    } else if (type === 'object' && data !== null) {
      const properties = {};
      const required = [];

      for (const [key, value] of Object.entries(data)) {
        properties[key] = this.inferSchema(value, key);
        required.push(key);
      }

      return {
        type: 'object',
        properties,
        required,
        additionalProperties: false
      };
    } else if (type === 'string') {
      // Detect formats
      const formats = this._detectStringFormat(data);
      return formats ? { type: 'string', format: formats } : { type: 'string' };
    } else if (type === 'number') {
      return {
        type: Number.isInteger(data) ? 'integer' : 'number',
        minimum: data,
        maximum: data
      };
    } else {
      return { type };
    }
  }

  /**
   * Generate synthetic JSON data based on schema or pattern
   */
  generateJSON(options = {}) {
    const {
      count = 10,
      template = null,
      schema = null,
      type = 'object',
      complexity = 'medium'
    } = options;

    const results = [];

    if (template) {
      // Generate based on template
      for (let i = 0; i < count; i++) {
        results.push(this._generateFromTemplate(template, i));
      }
    } else if (schema) {
      // Generate based on schema
      for (let i = 0; i < count; i++) {
        results.push(this._generateFromSchema(schema, i));
      }
    } else {
      // Generate generic data
      for (let i = 0; i < count; i++) {
        results.push(this._generateGenericData(type, complexity, i));
      }
    }

    return {
      success: true,
      count: results.length,
      data: results,
      format: count > 1 ? 'array' : 'single',
      message: `Generated ${count} record(s)`
    };
  }

  /**
   * Transform JSON data based on rules
   */
  transformJSON(jsonInput, transformations) {
    try {
      let data = typeof jsonInput === 'string' ? JSON.parse(jsonInput) : jsonInput;

      for (const transform of transformations) {
        data = this._applyTransformation(data, transform);
      }

      return {
        success: true,
        data,
        message: `Applied ${transformations.length} transformation(s)`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Process JSONL (JSON Lines) format
   */
  processJSONL(jsonlInput) {
    const lines = jsonlInput.trim().split('\n');
    const results = [];
    const errors = [];

    lines.forEach((line, index) => {
      if (line.trim()) {
        try {
          const parsed = JSON.parse(line);
          results.push(parsed);
        } catch (error) {
          errors.push({
            line: index + 1,
            content: line,
            error: error.message
          });
        }
      }
    });

    return {
      success: errors.length === 0,
      totalLines: lines.length,
      validLines: results.length,
      errors,
      data: results,
      message: `Processed ${results.length}/${lines.length} lines successfully`
    };
  }

  // ============ HELPER METHODS ============

  _analyzeStructure(data, depth = 0, maxDepth = 10) {
    if (depth > maxDepth) return { truncated: true };

    const type = Array.isArray(data) ? 'array' : typeof data;

    if (type === 'array') {
      return {
        type: 'array',
        length: data.length,
        itemTypes: [...new Set(data.map(item => typeof item))],
        sample: data.length > 0 ? this._analyzeStructure(data[0], depth + 1, maxDepth) : null
      };
    } else if (type === 'object' && data !== null) {
      const keys = Object.keys(data);
      return {
        type: 'object',
        keyCount: keys.length,
        keys,
        properties: Object.fromEntries(
          keys.slice(0, 20).map(key => [
            key,
            this._analyzeStructure(data[key], depth + 1, maxDepth)
          ])
        )
      };
    } else {
      return { type, value: type === 'string' && data.length > 100 ? data.slice(0, 100) + '...' : data };
    }
  }

  _computeStatistics(data) {
    const stats = {
      totalSize: JSON.stringify(data).length,
      depth: this._computeDepth(data),
      nodeCount: this._countNodes(data)
    };

    if (Array.isArray(data)) {
      stats.arrayLength = data.length;
      stats.uniqueTypes = [...new Set(data.map(item => typeof item))];
    } else if (typeof data === 'object' && data !== null) {
      stats.keyCount = Object.keys(data).length;
    }

    return stats;
  }

  _computeDepth(data, current = 0) {
    if (typeof data !== 'object' || data === null) return current;

    if (Array.isArray(data)) {
      return Math.max(current, ...data.map(item => this._computeDepth(item, current + 1)));
    } else {
      return Math.max(current, ...Object.values(data).map(val => this._computeDepth(val, current + 1)));
    }
  }

  _countNodes(data) {
    if (typeof data !== 'object' || data === null) return 1;

    if (Array.isArray(data)) {
      return 1 + data.reduce((sum, item) => sum + this._countNodes(item), 0);
    } else {
      return 1 + Object.values(data).reduce((sum, val) => sum + this._countNodes(val), 0);
    }
  }

  _detectStringFormat(str) {
    // Email
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str)) return 'email';
    // URL
    if (/^https?:\/\/.+/.test(str)) return 'uri';
    // Date
    if (/^\d{4}-\d{2}-\d{2}/.test(str)) return 'date';
    // UUID
    if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str)) return 'uuid';
    return null;
  }

  _mergeSchemas(schemas) {
    if (schemas.length === 0) return {};
    if (schemas.length === 1) return schemas[0];

    // Simple merge - take first schema as base
    return schemas[0];
  }

  _generateFromTemplate(template, index) {
    const result = JSON.parse(JSON.stringify(template)); // Deep clone

    // Replace placeholders
    return this._replacePlaceholders(result, index);
  }

  _replacePlaceholders(obj, index) {
    if (typeof obj === 'string') {
      return obj
        .replace(/\{\{index\}\}/g, index)
        .replace(/\{\{random\}\}/g, Math.floor(Math.random() * 1000))
        .replace(/\{\{uuid\}\}/g, this._generateUUID())
        .replace(/\{\{timestamp\}\}/g, Date.now());
    } else if (Array.isArray(obj)) {
      return obj.map(item => this._replacePlaceholders(item, index));
    } else if (typeof obj === 'object' && obj !== null) {
      const result = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = this._replacePlaceholders(value, index);
      }
      return result;
    }
    return obj;
  }

  _generateFromSchema(schema, index) {
    switch (schema.type) {
      case 'object':
        const obj = {};
        for (const [key, propSchema] of Object.entries(schema.properties || {})) {
          obj[key] = this._generateFromSchema(propSchema, index);
        }
        return obj;

      case 'array':
        const length = schema.minItems || 3;
        return Array.from({ length }, (_, i) =>
          this._generateFromSchema(schema.items || { type: 'string' }, index)
        );

      case 'string':
        if (schema.format === 'email') return `user${index}@example.com`;
        if (schema.format === 'uri') return `https://example.com/resource/${index}`;
        if (schema.format === 'uuid') return this._generateUUID();
        if (schema.format === 'date') return new Date().toISOString().split('T')[0];
        return `value_${index}`;

      case 'integer':
      case 'number':
        return index + 1;

      case 'boolean':
        return index % 2 === 0;

      default:
        return null;
    }
  }

  _generateGenericData(type, complexity, index) {
    if (type === 'array') {
      return Array.from({ length: 5 }, (_, i) => ({
        id: index * 5 + i,
        name: `Item ${index * 5 + i}`,
        value: Math.random() * 100,
        timestamp: Date.now()
      }));
    } else {
      return {
        id: index,
        name: `Record ${index}`,
        email: `user${index}@example.com`,
        age: 20 + Math.floor(Math.random() * 50),
        active: index % 2 === 0,
        score: Math.random() * 100,
        tags: [`tag${index % 5}`, `category${index % 3}`],
        metadata: {
          created: new Date().toISOString(),
          updated: new Date().toISOString(),
          version: 1
        }
      };
    }
  }

  _generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  _applyTransformation(data, transform) {
    // Simple transformation logic
    const { type, path, value } = transform;

    switch (type) {
      case 'add_field':
        if (typeof data === 'object' && !Array.isArray(data)) {
          data[path] = value;
        }
        break;

      case 'remove_field':
        if (typeof data === 'object' && !Array.isArray(data)) {
          delete data[path];
        }
        break;

      case 'rename_field':
        if (typeof data === 'object' && !Array.isArray(data) && data[path]) {
          data[value] = data[path];
          delete data[path];
        }
        break;
    }

    return data;
  }

  _generateRecommendations(data) {
    const recommendations = [];
    const size = JSON.stringify(data).length;

    if (size > 1000000) {
      recommendations.push('Large JSON detected. Consider splitting into smaller files or using JSONL format.');
    }

    if (this._computeDepth(data) > 10) {
      recommendations.push('Deep nesting detected. Consider flattening structure for better performance.');
    }

    if (Array.isArray(data) && data.length > 1000) {
      recommendations.push('Large array detected. Consider pagination or streaming for better performance.');
    }

    return recommendations;
  }

  _suggestFix(jsonInput, error) {
    const suggestions = [];

    if (error.message.includes('Unexpected token')) {
      suggestions.push('Check for missing or extra commas, quotes, or brackets');
    }

    if (error.message.includes('Unexpected end of JSON')) {
      suggestions.push('Check for missing closing brackets or braces');
    }

    return suggestions.length > 0 ? suggestions.join('; ') : 'Try using the fix operation for automatic repair';
  }
}

// ============ AGENT PLUGIN EXPORT ============

module.exports = {
  name: "json-ai-processor",
  startupConfig: {
    params: {}
  },
  plugin: function () {
    const processor = new JSONAIProcessor();

    return {
      name: this.name,
      setup(aibitat) {
        aibitat.function({
          name: "json_process",
          description: "Advanced JSON/JSONL processor with validation, error fixing, analysis, schema inference, and intelligent data generation. Operations: 'validate', 'fix', 'analyze', 'generate', 'infer_schema', 'transform', 'jsonl'",
          parameters: {
            $schema: "http://json-schema.org/draft-07/schema#",
            type: "object",
            properties: {
              operation: {
                type: "string",
                enum: ["validate", "fix", "analyze", "generate", "infer_schema", "transform", "jsonl"],
                description: "Operation to perform: validate (check syntax/schema), fix (auto-repair errors), analyze (deep structure analysis), generate (create synthetic data), infer_schema (extract JSON Schema), transform (modify structure), jsonl (process JSON Lines)"
              },
              json_input: {
                type: "string",
                description: "JSON or JSONL string to process. Required for all operations except 'generate'"
              },
              options: {
                type: "string",
                description: "JSON string with options. For generate: {count:1000,template:{...},schema:{...}}. For validate: {schema:{...}}. For transform: {transformations:[...]}"
              }
            },
            required: ["operation"],
            additionalProperties: false
          },
          handler: async function ({ operation, json_input, options }) {
            try {
              const opts = options ? JSON.parse(options) : {};

              let result;

              switch (operation) {
                case 'validate':
                  result = processor.validateJSON(json_input, opts.schema);
                  break;

                case 'fix':
                  result = processor.fixJSON(json_input);
                  break;

                case 'analyze':
                  result = processor.analyzeJSON(json_input);
                  break;

                case 'generate':
                  result = processor.generateJSON(opts);
                  break;

                case 'infer_schema':
                  const data = JSON.parse(json_input);
                  result = {
                    success: true,
                    schema: processor.inferSchema(data),
                    message: 'Schema inferred successfully'
                  };
                  break;

                case 'transform':
                  result = processor.transformJSON(json_input, opts.transformations || []);
                  break;

                case 'jsonl':
                  result = processor.processJSONL(json_input);
                  break;

                default:
                  result = {
                    success: false,
                    error: `Unknown operation: ${operation}`
                  };
              }

              // Return as formatted string
              return JSON.stringify(result, null, 2);
            } catch (error) {
              return JSON.stringify({
                success: false,
                error: error.message,
                operation
              }, null, 2);
            }
          }
        });
      }
    };
  }
};
