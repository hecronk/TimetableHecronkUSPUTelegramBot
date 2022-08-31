from app.bot.bot import dp, executor

executor.start_polling(dp, skip_updates=True)
