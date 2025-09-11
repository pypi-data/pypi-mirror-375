def check_answer(questionName, perm=False):
    """

    Parameters
    ==========
    question: str
       name of the MathQuestion.MathQuestion instance to be checked
    """
    from .varchecks import check_vars
    from .utils import get_internal

    question = get_internal(questionName)
    vars = question.solve()

    for var in vars:
        check_vars(var, vars[var], suppress_expected=True, perm=perm)
