from enum import Enum


class RegisterUserResult(Enum):
    Success = 0,
    MobileExists = 1


class ActivateMobileResult(Enum):
    Success = 0,
    NotFound = 1,
    NotMatch = 2,


class LoginUserResult(Enum):
    Success = 0,
    NotFound = 1,
    NotActivated = 2


class ForgotPasswordResult(Enum):
    Success = 0,
    NotFound = 1,


class ChangePasswordResult(Enum):
    Success = 0,
    CurrentPassNotCorrect = 1,
    CurrentPassIsNewCorrect = 2