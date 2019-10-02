function c$() {
    c$ = VUe;
    !!(Y$(),
    X$)
}

function Y$() {
    Y$ = VUe;
    var a, b;
    b = !b_();
    a = new j_;
    X$ = b ? new c_ : a
}



function f$(b) {
    c$();
    return function() {
        return g$(b, this, arguments);
        var a
    }
}

g$(f())

function g$(b, c, d) {
    var e, f;
    e = e$();
    try {
        if (OY) {
            try {
                return d$(b, c, d)
            } catch (a) {
                a = lUe(a);
                if (ZTb(a, 107)) {
                    f = a;
                    j$(f);
                    return undefined
                } else
                    throw mUe(a)
            }
        } else {
            return d$(b, c, d)
        }
    } finally {
        h$(e)
    }
}

function e$() {
    var a;
    if ($Z != 0) {
        a = bZ();
        if (a - a$ > xtt) {
            a$ = a;
            b$ = $wnd.setTimeout(l$, 10)
        }
    }
    if ($Z++ == 0) {
        x$((w$(),
        v$));
        return true
    }
    return false
}

function h$(a) {
    a && y$((w$(),
    v$));
    --$Z;
    if (a) {
        if (b$ != -1) {
            k$(b$);
            b$ = -1
        }
    }
}
