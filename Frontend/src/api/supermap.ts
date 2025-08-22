import type { ServiceResponse } from '@/types/map'
import { createAPIConfig } from '@/utils/config'

export class SuperMapError extends Error {
  constructor(
    message: string,
    public code?: number,
    public type: 'network' | 'service' | 'timeout' = 'service'
  ) {
    super(message)
    this.name = 'SuperMapError'
  }
}

export class SuperMapClient {
  private config = createAPIConfig()
  
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    retries: number = this.config.retryCount
  ): Promise<T> {
    try {
      return await operation()
    } catch (error) {
      if (retries > 0 && this.shouldRetry(error)) {
        await this.delay(Math.pow(2, this.config.retryCount - retries) * 1000) // 指数退避
        return this.executeWithRetry(operation, retries - 1)
      }
      throw error
    }
  }

  private shouldRetry(error: any): boolean {
    // 网络错误或超时错误可以重试
    return error instanceof SuperMapError && 
           (error.type === 'network' || error.type === 'timeout')
  }

  private createTimeoutPromise<T>(ms: number): Promise<T> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new SuperMapError('请求超时', 408, 'timeout')), ms)
    })
  }

  async checkServiceHealth(): Promise<ServiceResponse<boolean>> {
    return this.executeWithRetry(async () => {
      try {
        // 使用服务根URL进行健康检查
        const testUrl = `${this.config.baseUrl}/iserver/services/map-WuHan/rest/maps/武汉`
        const response = await fetch(testUrl, { 
          method: 'HEAD',
          signal: AbortSignal.timeout(this.config.timeout)
        })
        
        return {
          success: response.ok,
          data: response.ok,
          error: response.ok ? undefined : `HTTP ${response.status}`
        }
      } catch (error) {
        return {
          success: false,
          data: false,
          error: error instanceof Error ? error.message : '服务健康检查失败'
        }
      }
    })
  }
}

export const superMapClient = new SuperMapClient()