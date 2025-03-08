/**
 * A sample class to demonstrate various code patterns
 */
class Calculator {
  private value: number;

  constructor(initialValue: number = 0) {
    this.value = initialValue;
  }

  /**
   * Adds a number to the current value
   * @param num - The number to add
   * @returns The new value
   */
  add(num: number): number {
    this.value += num;
    return this.value;
  }

  /**
   * Performs a complex calculation based on conditions
   */
  complexOperation(x: number): number {
    if (x < 0) {
      return this.value;
    } else if (x > 100) {
      for (let i = 0; i < 10; i++) {
        if (i % 2 === 0) {
          this.value += i;
        } else {
          this.value -= i;
        }
      }
      return this.value;
    } else {
      while (x > 0) {
        this.value += x;
        x--;
      }
      return this.value;
    }
  }
} 