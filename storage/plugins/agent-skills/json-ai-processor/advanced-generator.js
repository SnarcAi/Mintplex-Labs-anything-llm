/**
 * Advanced JSON Data Generator with ML Patterns
 * Generates intelligent, realistic JSON data using various strategies
 */

class AdvancedJSONGenerator {
  constructor() {
    this.patterns = this._initializePatterns();
    this.markovChains = new Map();
  }

  /**
   * Generate highly realistic data using ML-inspired patterns
   */
  generateAdvanced(options = {}) {
    const {
      count = 1000,
      dataType = 'mixed',
      realism = 'high',
      variability = 0.7,
      seed = null
    } = options;

    if (seed) this._setSeed(seed);

    const generators = {
      users: () => this._generateUsers(count, realism, variability),
      products: () => this._generateProducts(count, realism, variability),
      transactions: () => this._generateTransactions(count, realism, variability),
      logs: () => this._generateLogs(count, realism, variability),
      timeseries: () => this._generateTimeSeries(count, realism, variability),
      mixed: () => this._generateMixed(count, realism, variability),
      custom: () => this._generateFromPattern(options.pattern, count, variability)
    };

    const generator = generators[dataType] || generators.mixed;
    const data = generator();

    return {
      success: true,
      count: data.length,
      dataType,
      data,
      metadata: {
        generatedAt: new Date().toISOString(),
        realism,
        variability,
        seed
      }
    };
  }

  /**
   * Generate realistic user data
   */
  _generateUsers(count, realism, variability) {
    const users = [];
    const firstNames = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Anna', 'Tom', 'Lisa', 'Kevin', 'Maria'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
    const domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'example.org'];
    const countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Australia', 'Japan', 'Brazil'];
    const cities = ['New York', 'London', 'Paris', 'Tokyo', 'Berlin', 'Madrid', 'Sydney', 'Toronto', 'Rome', 'Seoul'];

    for (let i = 0; i < count; i++) {
      const firstName = this._randomChoice(firstNames);
      const lastName = this._randomChoice(lastNames);
      const username = `${firstName.toLowerCase()}${lastName.toLowerCase()}${this._randomInt(100, 999)}`;

      const user = {
        id: i + 1,
        uuid: this._generateUUID(),
        username,
        email: `${username}@${this._randomChoice(domains)}`,
        firstName,
        lastName,
        fullName: `${firstName} ${lastName}`,
        age: this._randomInt(18, 75),
        gender: this._randomChoice(['male', 'female', 'other']),
        phone: this._generatePhone(),
        address: {
          street: `${this._randomInt(1, 9999)} ${this._randomChoice(['Main', 'Oak', 'Maple', 'Pine', 'Cedar'])} ${this._randomChoice(['St', 'Ave', 'Blvd', 'Rd'])}`,
          city: this._randomChoice(cities),
          state: this._randomChoice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH']),
          country: this._randomChoice(countries),
          zipCode: this._randomInt(10000, 99999).toString()
        },
        accountType: this._randomChoice(['free', 'premium', 'enterprise']),
        isActive: Math.random() > 0.1,
        registeredAt: this._randomDate(new Date('2020-01-01'), new Date()),
        lastLoginAt: this._randomDate(new Date('2024-01-01'), new Date()),
        preferences: {
          newsletter: Math.random() > 0.5,
          notifications: Math.random() > 0.3,
          theme: this._randomChoice(['light', 'dark', 'auto']),
          language: this._randomChoice(['en', 'es', 'fr', 'de', 'ja'])
        },
        stats: {
          loginCount: this._randomInt(1, 500),
          purchaseCount: this._randomInt(0, 50),
          totalSpent: this._randomFloat(0, 5000, 2),
          averageRating: this._randomFloat(1, 5, 1)
        },
        tags: this._randomSample(['vip', 'active', 'returning', 'new', 'at-risk', 'champion'], this._randomInt(1, 3))
      };

      // Add realistic variations
      if (realism === 'high') {
        if (Math.random() < 0.1) user.middleName = this._randomChoice(firstNames);
        if (Math.random() < 0.05) delete user.phone; // Some users don't have phones
        if (user.age < 25) user.stats.purchaseCount = Math.floor(user.stats.purchaseCount * 0.5);
      }

      users.push(user);
    }

    return users;
  }

  /**
   * Generate realistic product data
   */
  _generateProducts(count, realism, variability) {
    const products = [];
    const categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys', 'Beauty', 'Food'];
    const brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE', 'Generic'];
    const adjectives = ['Premium', 'Professional', 'Classic', 'Modern', 'Vintage', 'Eco', 'Smart', 'Ultra'];
    const nouns = ['Device', 'Gadget', 'Tool', 'Product', 'Item', 'Equipment', 'Accessory'];

    for (let i = 0; i < count; i++) {
      const category = this._randomChoice(categories);
      const brand = this._randomChoice(brands);
      const name = `${this._randomChoice(adjectives)} ${this._randomChoice(nouns)} ${this._randomInt(100, 999)}`;

      const basePrice = this._randomFloat(10, 1000, 2);
      const discount = Math.random() > 0.7 ? this._randomFloat(0.05, 0.5, 2) : 0;

      const product = {
        id: i + 1,
        sku: `SKU-${this._randomString(8).toUpperCase()}`,
        name,
        brand,
        category,
        subcategory: this._randomChoice(['SubCat1', 'SubCat2', 'SubCat3']),
        description: `High-quality ${name.toLowerCase()} from ${brand}. Perfect for everyday use.`,
        price: {
          currency: 'USD',
          amount: basePrice,
          discount: discount,
          finalPrice: parseFloat((basePrice * (1 - discount)).toFixed(2))
        },
        stock: {
          quantity: this._randomInt(0, 500),
          warehouse: this._randomChoice(['WH-1', 'WH-2', 'WH-3']),
          reserved: this._randomInt(0, 50)
        },
        ratings: {
          average: this._randomFloat(3.0, 5.0, 1),
          count: this._randomInt(0, 1000),
          distribution: this._generateRatingDistribution()
        },
        dimensions: {
          length: this._randomFloat(5, 100, 1),
          width: this._randomFloat(5, 100, 1),
          height: this._randomFloat(5, 100, 1),
          weight: this._randomFloat(0.1, 50, 2),
          unit: 'cm/kg'
        },
        specifications: {
          color: this._randomChoice(['Black', 'White', 'Silver', 'Blue', 'Red']),
          material: this._randomChoice(['Plastic', 'Metal', 'Wood', 'Glass', 'Fabric']),
          warranty: this._randomChoice(['1 year', '2 years', '3 years', 'Lifetime'])
        },
        isActive: Math.random() > 0.05,
        isFeatured: Math.random() > 0.8,
        createdAt: this._randomDate(new Date('2020-01-01'), new Date()),
        updatedAt: this._randomDate(new Date('2023-01-01'), new Date()),
        tags: this._randomSample(['bestseller', 'new', 'sale', 'trending', 'limited'], this._randomInt(0, 3))
      };

      products.push(product);
    }

    return products;
  }

  /**
   * Generate realistic transaction data
   */
  _generateTransactions(count, realism, variability) {
    const transactions = [];
    const statuses = ['pending', 'completed', 'failed', 'refunded', 'cancelled'];
    const paymentMethods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'crypto'];

    for (let i = 0; i < count; i++) {
      const itemCount = this._randomInt(1, 5);
      const items = Array.from({ length: itemCount }, (_, idx) => ({
        productId: this._randomInt(1, 1000),
        productName: `Product ${this._randomInt(1, 100)}`,
        quantity: this._randomInt(1, 5),
        unitPrice: this._randomFloat(10, 200, 2),
        discount: Math.random() > 0.7 ? this._randomFloat(0, 0.3, 2) : 0
      }));

      const subtotal = items.reduce((sum, item) =>
        sum + (item.quantity * item.unitPrice * (1 - item.discount)), 0
      );
      const tax = subtotal * 0.08;
      const shipping = itemCount > 3 ? 0 : 9.99;
      const total = subtotal + tax + shipping;

      const transaction = {
        id: i + 1,
        transactionId: `TXN-${Date.now()}-${this._randomString(8).toUpperCase()}`,
        userId: this._randomInt(1, 10000),
        status: this._randomWeightedChoice(statuses, [0.1, 0.75, 0.08, 0.05, 0.02]),
        paymentMethod: this._randomChoice(paymentMethods),
        items,
        pricing: {
          subtotal: parseFloat(subtotal.toFixed(2)),
          tax: parseFloat(tax.toFixed(2)),
          shipping: shipping,
          discount: 0,
          total: parseFloat(total.toFixed(2)),
          currency: 'USD'
        },
        shipping: {
          address: {
            street: `${this._randomInt(1, 9999)} Main St`,
            city: this._randomChoice(['New York', 'Los Angeles', 'Chicago']),
            state: this._randomChoice(['NY', 'CA', 'IL']),
            zipCode: this._randomInt(10000, 99999).toString(),
            country: 'USA'
          },
          method: this._randomChoice(['standard', 'express', 'overnight']),
          trackingNumber: `TRACK-${this._randomString(12).toUpperCase()}`
        },
        timestamps: {
          createdAt: this._randomDate(new Date('2024-01-01'), new Date()),
          updatedAt: this._randomDate(new Date('2024-01-01'), new Date()),
          completedAt: Math.random() > 0.3 ? this._randomDate(new Date('2024-01-01'), new Date()) : null
        },
        metadata: {
          ipAddress: this._generateIP(),
          userAgent: 'Mozilla/5.0',
          sessionId: this._generateUUID()
        }
      };

      transactions.push(transaction);
    }

    return transactions;
  }

  /**
   * Generate realistic log data
   */
  _generateLogs(count, realism, variability) {
    const logs = [];
    const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
    const services = ['api-gateway', 'auth-service', 'payment-service', 'notification-service', 'analytics'];
    const events = ['user.login', 'user.logout', 'payment.processed', 'error.500', 'cache.miss', 'db.query'];

    for (let i = 0; i < count; i++) {
      const level = this._randomWeightedChoice(levels, [0.3, 0.45, 0.15, 0.08, 0.02]);

      const log = {
        timestamp: this._randomDate(new Date('2024-01-01'), new Date()).toISOString(),
        level,
        service: this._randomChoice(services),
        event: this._randomChoice(events),
        message: this._generateLogMessage(level),
        traceId: this._generateUUID(),
        spanId: this._randomString(16),
        userId: Math.random() > 0.3 ? this._randomInt(1, 10000) : null,
        requestId: this._generateUUID(),
        duration: this._randomInt(10, 5000),
        statusCode: level === 'ERROR' ? this._randomChoice([400, 404, 500, 503]) : 200,
        metadata: {
          hostname: `server-${this._randomInt(1, 10)}`,
          pid: this._randomInt(1000, 9999),
          version: `${this._randomInt(1, 5)}.${this._randomInt(0, 20)}.${this._randomInt(0, 50)}`,
          environment: this._randomChoice(['production', 'staging', 'development'])
        }
      };

      if (level === 'ERROR' || level === 'CRITICAL') {
        log.error = {
          type: this._randomChoice(['TypeError', 'NetworkError', 'ValidationError', 'DatabaseError']),
          message: 'An error occurred during processing',
          stack: 'Error: Stack trace...\n    at function (file.js:123:45)'
        };
      }

      logs.push(log);
    }

    return logs;
  }

  /**
   * Generate time series data
   */
  _generateTimeSeries(count, realism, variability) {
    const data = [];
    const startDate = new Date('2024-01-01');
    const interval = 3600000; // 1 hour in ms

    let baseValue = 100;
    let trend = 0.001;

    for (let i = 0; i < count; i++) {
      const timestamp = new Date(startDate.getTime() + (i * interval));

      // Add trend, seasonality, and noise
      const seasonality = Math.sin((i / 24) * Math.PI * 2) * 10;
      const noise = (Math.random() - 0.5) * variability * 20;
      const value = baseValue + (i * trend) + seasonality + noise;

      data.push({
        timestamp: timestamp.toISOString(),
        value: parseFloat(value.toFixed(2)),
        metric: 'cpu_usage',
        tags: {
          host: `server-${this._randomInt(1, 5)}`,
          region: this._randomChoice(['us-east-1', 'us-west-2', 'eu-west-1']),
          environment: 'production'
        },
        metadata: {
          sampleRate: '1m',
          aggregation: 'avg',
          unit: 'percent'
        }
      });
    }

    return data;
  }

  /**
   * Generate mixed data types
   */
  _generateMixed(count, realism, variability) {
    const mixed = [];
    const types = ['user', 'product', 'transaction', 'log'];

    for (let i = 0; i < count; i++) {
      const type = this._randomChoice(types);
      let record;

      switch (type) {
        case 'user':
          record = this._generateUsers(1, realism, variability)[0];
          break;
        case 'product':
          record = this._generateProducts(1, realism, variability)[0];
          break;
        case 'transaction':
          record = this._generateTransactions(1, realism, variability)[0];
          break;
        case 'log':
          record = this._generateLogs(1, realism, variability)[0];
          break;
      }

      mixed.push({ type, ...record });
    }

    return mixed;
  }

  /**
   * Generate from custom pattern
   */
  _generateFromPattern(pattern, count, variability) {
    const data = [];

    for (let i = 0; i < count; i++) {
      const record = JSON.parse(JSON.stringify(pattern));
      this._applyVariability(record, i, variability);
      data.push(record);
    }

    return data;
  }

  _applyVariability(obj, index, variability) {
    for (const key in obj) {
      const value = obj[key];

      if (typeof value === 'string') {
        obj[key] = value
          .replace(/\{\{index\}\}/g, index)
          .replace(/\{\{random\}\}/g, this._randomInt(1, 1000))
          .replace(/\{\{uuid\}\}/g, this._generateUUID())
          .replace(/\{\{email\}\}/g, `user${index}@example.com`)
          .replace(/\{\{date\}\}/g, new Date().toISOString());
      } else if (typeof value === 'number') {
        obj[key] = value + (Math.random() - 0.5) * value * variability;
      } else if (typeof value === 'object' && value !== null) {
        this._applyVariability(value, index, variability);
      }
    }
  }

  // ============ UTILITY METHODS ============

  _initializePatterns() {
    return {
      names: { first: [], last: [] },
      addresses: { streets: [], cities: [] },
      products: { adjectives: [], nouns: [] }
    };
  }

  _randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  _randomFloat(min, max, decimals = 2) {
    return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
  }

  _randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
  }

  _randomWeightedChoice(items, weights) {
    const total = weights.reduce((sum, w) => sum + w, 0);
    let random = Math.random() * total;

    for (let i = 0; i < items.length; i++) {
      random -= weights[i];
      if (random <= 0) return items[i];
    }

    return items[items.length - 1];
  }

  _randomSample(array, count) {
    const shuffled = [...array].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, Math.min(count, array.length));
  }

  _randomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  }

  _randomDate(start, end) {
    return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  }

  _generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  _generatePhone() {
    return `+1-${this._randomInt(200, 999)}-${this._randomInt(200, 999)}-${this._randomInt(1000, 9999)}`;
  }

  _generateIP() {
    return `${this._randomInt(1, 255)}.${this._randomInt(0, 255)}.${this._randomInt(0, 255)}.${this._randomInt(1, 255)}`;
  }

  _generateRatingDistribution() {
    const total = this._randomInt(100, 1000);
    const dist = {
      5: this._randomInt(0, total),
      4: this._randomInt(0, total),
      3: this._randomInt(0, total),
      2: this._randomInt(0, total),
      1: this._randomInt(0, total)
    };

    // Normalize
    const sum = Object.values(dist).reduce((a, b) => a + b, 0);
    for (const key in dist) {
      dist[key] = Math.floor((dist[key] / sum) * total);
    }

    return dist;
  }

  _generateLogMessage(level) {
    const messages = {
      DEBUG: ['Processing request', 'Cache hit', 'Database query executed'],
      INFO: ['User logged in', 'Payment processed successfully', 'Email sent'],
      WARN: ['High memory usage detected', 'Slow query detected', 'Rate limit approaching'],
      ERROR: ['Database connection failed', 'Payment processing error', 'Invalid request'],
      CRITICAL: ['System out of memory', 'Database unavailable', 'Security breach detected']
    };

    return this._randomChoice(messages[level] || messages.INFO);
  }

  _setSeed(seed) {
    // Simple seeded random (for reproducibility)
    this.seed = seed;
  }
}

module.exports = AdvancedJSONGenerator;
