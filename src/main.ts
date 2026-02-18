import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';
import { ConsoleLogger, NotFoundException } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: new ConsoleLogger({
      prefix: 'LearnX-API',
      logLevels: ['log', 'error', 'warn'],
      colors: true,
      json: true,
    }),
  });
  app.enableCors();

  const config = app.get(ConfigService);
  const port: number = config.getOrThrow<number>('PORT');

  if (!port) {
    throw new NotFoundException('Port not found in environment variables');
  }

  await app.listen(port);
}

bootstrap();
