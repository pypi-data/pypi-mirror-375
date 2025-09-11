import { i as de, a as W, r as fe, Z as R, g as me, b as _e } from "./Index-Dv_wZGHf.js";
const E = window.ms_globals.React, le = window.ms_globals.React.useMemo, ee = window.ms_globals.React.useRef, ce = window.ms_globals.React.useCallback, ae = window.ms_globals.React.forwardRef, ue = window.ms_globals.React.useState, j = window.ms_globals.React.useEffect, N = window.ms_globals.ReactDOM.createPortal, pe = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, z = window.ms_globals.antd.Form;
var ge = /\s/;
function be(t) {
  for (var e = t.length; e-- && ge.test(t.charAt(e)); )
    ;
  return e;
}
var we = /^\s+/;
function ye(t) {
  return t && t.slice(0, be(t) + 1).replace(we, "");
}
var U = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, xe = /^0o[0-7]+$/i, Ce = parseInt;
function B(t) {
  if (typeof t == "number")
    return t;
  if (de(t))
    return U;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ye(t);
  var r = ve.test(t);
  return r || xe.test(t) ? Ce(t.slice(2), r ? 2 : 8) : Ee.test(t) ? U : +t;
}
var O = function() {
  return fe.Date.now();
}, Se = "Expected a function", Ie = Math.max, ke = Math.min;
function Re(t, e, r) {
  var i, s, n, o, l, u, p = 0, m = !1, c = !1, g = !0;
  if (typeof t != "function")
    throw new TypeError(Se);
  e = B(e) || 0, W(r) && (m = !!r.leading, c = "maxWait" in r, n = c ? Ie(B(r.maxWait) || 0, e) : n, g = "trailing" in r ? !!r.trailing : g);
  function f(d) {
    var x = i, k = s;
    return i = s = void 0, p = d, o = t.apply(k, x), o;
  }
  function b(d) {
    return p = d, l = setTimeout(h, e), m ? f(d) : o;
  }
  function w(d) {
    var x = d - u, k = d - p, D = e - x;
    return c ? ke(D, n - k) : D;
  }
  function _(d) {
    var x = d - u, k = d - p;
    return u === void 0 || x >= e || x < 0 || c && k >= n;
  }
  function h() {
    var d = O();
    if (_(d))
      return y(d);
    l = setTimeout(h, w(d));
  }
  function y(d) {
    return l = void 0, g && i ? f(d) : (i = s = void 0, o);
  }
  function I() {
    l !== void 0 && clearTimeout(l), p = 0, i = u = s = l = void 0;
  }
  function a() {
    return l === void 0 ? o : y(O());
  }
  function C() {
    var d = O(), x = _(d);
    if (i = arguments, s = this, u = d, x) {
      if (l === void 0)
        return b(u);
      if (c)
        return clearTimeout(l), l = setTimeout(h, e), f(u);
    }
    return l === void 0 && (l = setTimeout(h, e)), o;
  }
  return C.cancel = I, C.flush = a, C;
}
var te = {
  exports: {}
}, F = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Pe = E, Te = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Oe = Object.prototype.hasOwnProperty, Le = Pe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(t, e, r) {
  var i, s = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (i in e) Oe.call(e, i) && !je.hasOwnProperty(i) && (s[i] = e[i]);
  if (t && t.defaultProps) for (i in e = t.defaultProps, e) s[i] === void 0 && (s[i] = e[i]);
  return {
    $$typeof: Te,
    type: t,
    key: n,
    ref: o,
    props: s,
    _owner: Le.current
  };
}
F.Fragment = Fe;
F.jsx = ne;
F.jsxs = ne;
te.exports = F;
var v = te.exports;
const {
  SvelteComponent: Ne,
  assign: G,
  binding_callbacks: H,
  check_outros: We,
  children: re,
  claim_element: oe,
  claim_space: Ae,
  component_subscribe: q,
  compute_slots: Me,
  create_slot: De,
  detach: S,
  element: se,
  empty: K,
  exclude_internal_props: J,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ue,
  group_outros: Be,
  init: Ge,
  insert_hydration: P,
  safe_not_equal: He,
  set_custom_element_data: ie,
  space: qe,
  transition_in: T,
  transition_out: A,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(t) {
  let e, r;
  const i = (
    /*#slots*/
    t[7].default
  ), s = De(
    i,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = se("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      e = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = re(e);
      s && s.l(o), o.forEach(S), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      P(n, e, o), s && s.m(e, null), t[9](e), r = !0;
    },
    p(n, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && Ke(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        r ? Ue(
          i,
          /*$$scope*/
          n[6],
          o,
          null
        ) : ze(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (T(s, n), r = !0);
    },
    o(n) {
      A(s, n), r = !1;
    },
    d(n) {
      n && S(e), s && s.d(n), t[9](null);
    }
  };
}
function Qe(t) {
  let e, r, i, s, n = (
    /*$$slots*/
    t[4].default && X(t)
  );
  return {
    c() {
      e = se("react-portal-target"), r = qe(), n && n.c(), i = K(), this.h();
    },
    l(o) {
      e = oe(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(e).forEach(S), r = Ae(o), n && n.l(o), i = K(), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      P(o, e, l), t[8](e), P(o, r, l), n && n.m(o, l), P(o, i, l), s = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, l), l & /*$$slots*/
      16 && T(n, 1)) : (n = X(o), n.c(), T(n, 1), n.m(i.parentNode, i)) : n && (Be(), A(n, 1, 1, () => {
        n = null;
      }), We());
    },
    i(o) {
      s || (T(n), s = !0);
    },
    o(o) {
      A(n), s = !1;
    },
    d(o) {
      o && (S(e), S(r), S(i)), t[8](null), n && n.d(o);
    }
  };
}
function Y(t) {
  const {
    svelteInit: e,
    ...r
  } = t;
  return r;
}
function Ve(t, e, r) {
  let i, s, {
    $$slots: n = {},
    $$scope: o
  } = e;
  const l = Me(n);
  let {
    svelteInit: u
  } = e;
  const p = R(Y(e)), m = R();
  q(t, m, (a) => r(0, i = a));
  const c = R();
  q(t, c, (a) => r(1, s = a));
  const g = [], f = Xe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: w,
    subSlotIndex: _
  } = me() || {}, h = u({
    parent: f,
    props: p,
    target: m,
    slot: c,
    slotKey: b,
    slotIndex: w,
    subSlotIndex: _,
    onDestroy(a) {
      g.push(a);
    }
  });
  Ze("$$ms-gr-react-wrapper", h), Je(() => {
    p.set(Y(e));
  }), Ye(() => {
    g.forEach((a) => a());
  });
  function y(a) {
    H[a ? "unshift" : "push"](() => {
      i = a, m.set(i);
    });
  }
  function I(a) {
    H[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return t.$$set = (a) => {
    r(17, e = G(G({}, e), J(a))), "svelteInit" in a && r(5, u = a.svelteInit), "$$scope" in a && r(6, o = a.$$scope);
  }, e = J(e), [i, s, m, c, l, u, o, n, y, I];
}
class $e extends Ne {
  constructor(e) {
    super(), Ge(this, e, Ve, Qe, He, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ft
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, L = window.ms_globals.tree;
function et(t, e = {}) {
  function r(i) {
    const s = R(), n = new $e({
      ...i,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: t,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, u = o.parent ?? L;
          return u.nodes = [...u.nodes, l], Z({
            createPortal: N,
            node: L
          }), o.onDestroy(() => {
            u.nodes = u.nodes.filter((p) => p.svelteInstance !== s), Z({
              createPortal: N,
              node: L
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise.then(() => {
      i(r);
    });
  });
}
function tt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function nt(t, e = !1) {
  try {
    if (_e(t))
      return t;
    if (e && !tt(t))
      return;
    if (typeof t == "string") {
      let r = t.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Q(t, e) {
  return le(() => nt(t, e), [t, e]);
}
function rt(t) {
  const e = ee(t);
  return e.current = t, ce((...r) => {
    var i;
    return (i = e.current) == null ? void 0 : i.call(e, ...r);
  }, []);
}
const ot = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const i = t[r];
    return e[r] = it(r, i), e;
  }, {}) : {};
}
function it(t, e) {
  return typeof e == "number" && !ot.includes(t) ? e + "px" : e;
}
function M(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const s = E.Children.toArray(t._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = M(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return s.originalChildren = t._reactElement.props.children, e.push(N(E.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: s
    }), r)), {
      clonedElement: r,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((s) => {
    t.getEventListeners(s).forEach(({
      listener: o,
      type: l,
      useCapture: u
    }) => {
      r.addEventListener(l, o, u);
    });
  });
  const i = Array.from(t.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = M(n);
      e.push(...l), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const V = ae(({
  slot: t,
  clone: e,
  className: r,
  style: i,
  observeAttributes: s
}, n) => {
  const o = ee(), [l, u] = ue([]), {
    forceClone: p
  } = pe(), m = p ? !0 : e;
  return j(() => {
    var w;
    if (!o.current || !t)
      return;
    let c = t;
    function g() {
      let _ = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (_ = c.children[0], _.tagName.toLowerCase() === "react-portal-target" && _.children[0] && (_ = _.children[0])), lt(n, _), r && _.classList.add(...r.split(" ")), i) {
        const h = st(i);
        Object.keys(h).forEach((y) => {
          _.style[y] = h[y];
        });
      }
    }
    let f = null, b = null;
    if (m && window.MutationObserver) {
      let _ = function() {
        var a, C, d;
        (a = o.current) != null && a.contains(c) && ((C = o.current) == null || C.removeChild(c));
        const {
          portals: y,
          clonedElement: I
        } = M(t);
        c = I, u(y), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          g();
        }, 50), (d = o.current) == null || d.appendChild(c);
      };
      _();
      const h = Re(() => {
        _(), f == null || f.disconnect(), f == null || f.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      f = new window.MutationObserver(h), f.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (w = o.current) == null || w.appendChild(c);
    return () => {
      var _, h;
      c.style.display = "", (_ = o.current) != null && _.contains(c) && ((h = o.current) == null || h.removeChild(c)), f == null || f.disconnect();
    };
  }, [t, m, r, i, n, s, p]), E.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
}), ct = ({
  children: t,
  ...e
}) => /* @__PURE__ */ v.jsx(v.Fragment, {
  children: t(e)
});
function at(t) {
  return E.createElement(ct, {
    children: t
  });
}
function $(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? at((r) => /* @__PURE__ */ v.jsx(he, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ v.jsx(V, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ v.jsx(V, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ut({
  key: t,
  slots: e,
  targets: r
}, i) {
  return e[t] ? (...s) => r ? r.map((n, o) => /* @__PURE__ */ v.jsx(E.Fragment, {
    children: $(n, {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ v.jsx(v.Fragment, {
    children: $(e[t], {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }) : void 0;
}
const mt = et(({
  value: t,
  formAction: e,
  onValueChange: r,
  requiredMark: i,
  onValuesChange: s,
  feedbackIcons: n,
  setSlotParams: o,
  slots: l,
  onResetFormAction: u,
  ...p
}) => {
  const [m] = z.useForm(), c = Q(n), g = Q(i), f = rt(u);
  return j(() => {
    switch (e) {
      case "reset":
        m.resetFields();
        break;
      case "submit":
        m.submit();
        break;
      case "validate":
        m.validateFields();
        break;
    }
    f();
  }, [m, e, f]), j(() => {
    t ? m.setFieldsValue(t) : m.resetFields();
  }, [m, t]), /* @__PURE__ */ v.jsx(z, {
    ...p,
    form: m,
    requiredMark: l.requiredMark ? ut({
      key: "requiredMark",
      slots: l
    }) : i === "optional" ? i : g || i,
    feedbackIcons: c,
    onValuesChange: (b, w) => {
      r(w), s == null || s(b, w);
    }
  });
});
export {
  mt as Form,
  mt as default
};
