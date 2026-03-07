def log_args_kwargs(func):
    def wrapper(*args, **kwargs):
        print(f" Позиционные аргументы: {args}")
        print(f" Именованные аргументы: {kwargs}")
        return func
    return wrapper



@log_args_kwargs
def my_function(x, y, **kwargs):
    return x + y

my_function(10,20, debug="True", verbose="False")

