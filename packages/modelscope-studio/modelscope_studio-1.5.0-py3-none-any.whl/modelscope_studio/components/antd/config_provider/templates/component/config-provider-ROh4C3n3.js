import { i as Zr, a as Ve, r as Yr, Z as L, g as qr, b as Kr, c as ht, t as W, d as Qr } from "./Index-Bv07WiuH.js";
const N = window.ms_globals.React, Vr = window.ms_globals.React.forwardRef, Xr = window.ms_globals.React.useRef, Zt = window.ms_globals.React.useState, Yt = window.ms_globals.React.useEffect, Wr = window.ms_globals.React.useMemo, $e = window.ms_globals.ReactDOM.createPortal, Jr = window.ms_globals.internalContext.useContextPropsContext, en = window.ms_globals.internalContext.ContextPropsProvider, tn = window.ms_globals.antdCssinjs.StyleProvider, rn = window.ms_globals.antd.ConfigProvider, _t = window.ms_globals.antd.theme, qt = window.ms_globals.dayjs;
function Kt(e, t) {
  for (var r = 0; r < t.length; r++) {
    const n = t[r];
    if (typeof n != "string" && !Array.isArray(n)) {
      for (const i in n)
        if (i !== "default" && !(i in e)) {
          const a = Object.getOwnPropertyDescriptor(n, i);
          a && Object.defineProperty(e, i, a.get ? a : {
            enumerable: !0,
            get: () => n[i]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(e, Symbol.toStringTag, {
    value: "Module"
  }));
}
var nn = /\s/;
function an(e) {
  for (var t = e.length; t-- && nn.test(e.charAt(t)); )
    ;
  return t;
}
var on = /^\s+/;
function sn(e) {
  return e && e.slice(0, an(e) + 1).replace(on, "");
}
var yt = NaN, ln = /^[-+]0x[0-9a-f]+$/i, un = /^0b[01]+$/i, hn = /^0o[0-7]+$/i, cn = parseInt;
function bt(e) {
  if (typeof e == "number")
    return e;
  if (Zr(e))
    return yt;
  if (Ve(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Ve(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = sn(e);
  var r = un.test(e);
  return r || hn.test(e) ? cn(e.slice(2), r ? 2 : 8) : ln.test(e) ? yt : +e;
}
var Be = function() {
  return Yr.Date.now();
}, fn = "Expected a function", mn = Math.max, dn = Math.min;
function pn(e, t, r) {
  var n, i, a, o, s, u, h = 0, l = !1, c = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(fn);
  t = bt(t) || 0, Ve(r) && (l = !!r.leading, c = "maxWait" in r, a = c ? mn(bt(r.maxWait) || 0, t) : a, f = "trailing" in r ? !!r.trailing : f);
  function m(g) {
    var O = n, Y = i;
    return n = i = void 0, h = g, o = e.apply(Y, O), o;
  }
  function E(g) {
    return h = g, s = setTimeout(x, t), l ? m(g) : o;
  }
  function P(g) {
    var O = g - u, Y = g - h, pt = t - O;
    return c ? dn(pt, a - Y) : pt;
  }
  function b(g) {
    var O = g - u, Y = g - h;
    return u === void 0 || O >= t || O < 0 || c && Y >= a;
  }
  function x() {
    var g = Be();
    if (b(g))
      return w(g);
    s = setTimeout(x, P(g));
  }
  function w(g) {
    return s = void 0, f && n ? m(g) : (n = i = void 0, o);
  }
  function T() {
    s !== void 0 && clearTimeout(s), h = 0, n = u = i = s = void 0;
  }
  function _() {
    return s === void 0 ? o : w(Be());
  }
  function S() {
    var g = Be(), O = b(g);
    if (n = arguments, i = this, u = g, O) {
      if (s === void 0)
        return E(u);
      if (c)
        return clearTimeout(s), s = setTimeout(x, t), m(u);
    }
    return s === void 0 && (s = setTimeout(x, t)), o;
  }
  return S.cancel = T, S.flush = _, S;
}
var Qt = {
  exports: {}
}, ye = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var _n = N, yn = Symbol.for("react.element"), bn = Symbol.for("react.fragment"), gn = Object.prototype.hasOwnProperty, vn = _n.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, xn = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Jt(e, t, r) {
  var n, i = {}, a = null, o = null;
  r !== void 0 && (a = "" + r), t.key !== void 0 && (a = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (n in t) gn.call(t, n) && !xn.hasOwnProperty(n) && (i[n] = t[n]);
  if (e && e.defaultProps) for (n in t = e.defaultProps, t) i[n] === void 0 && (i[n] = t[n]);
  return {
    $$typeof: yn,
    type: e,
    key: a,
    ref: o,
    props: i,
    _owner: vn.current
  };
}
ye.Fragment = bn;
ye.jsx = Jt;
ye.jsxs = Jt;
Qt.exports = ye;
var I = Qt.exports;
const {
  SvelteComponent: En,
  assign: gt,
  binding_callbacks: vt,
  check_outros: Pn,
  children: er,
  claim_element: tr,
  claim_space: Sn,
  component_subscribe: xt,
  compute_slots: wn,
  create_slot: Tn,
  detach: F,
  element: rr,
  empty: Et,
  exclude_internal_props: Pt,
  get_all_dirty_from_scope: Hn,
  get_slot_changes: On,
  group_outros: An,
  init: Cn,
  insert_hydration: le,
  safe_not_equal: In,
  set_custom_element_data: nr,
  space: Bn,
  transition_in: ue,
  transition_out: Xe,
  update_slot_base: Nn
} = window.__gradio__svelte__internal, {
  beforeUpdate: Rn,
  getContext: Mn,
  onDestroy: Ln,
  setContext: jn
} = window.__gradio__svelte__internal;
function St(e) {
  let t, r;
  const n = (
    /*#slots*/
    e[7].default
  ), i = Tn(
    n,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = rr("svelte-slot"), i && i.c(), this.h();
    },
    l(a) {
      t = tr(a, "SVELTE-SLOT", {
        class: !0
      });
      var o = er(t);
      i && i.l(o), o.forEach(F), this.h();
    },
    h() {
      nr(t, "class", "svelte-1rt0kpf");
    },
    m(a, o) {
      le(a, t, o), i && i.m(t, null), e[9](t), r = !0;
    },
    p(a, o) {
      i && i.p && (!r || o & /*$$scope*/
      64) && Nn(
        i,
        n,
        a,
        /*$$scope*/
        a[6],
        r ? On(
          n,
          /*$$scope*/
          a[6],
          o,
          null
        ) : Hn(
          /*$$scope*/
          a[6]
        ),
        null
      );
    },
    i(a) {
      r || (ue(i, a), r = !0);
    },
    o(a) {
      Xe(i, a), r = !1;
    },
    d(a) {
      a && F(t), i && i.d(a), e[9](null);
    }
  };
}
function Dn(e) {
  let t, r, n, i, a = (
    /*$$slots*/
    e[4].default && St(e)
  );
  return {
    c() {
      t = rr("react-portal-target"), r = Bn(), a && a.c(), n = Et(), this.h();
    },
    l(o) {
      t = tr(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), er(t).forEach(F), r = Sn(o), a && a.l(o), n = Et(), this.h();
    },
    h() {
      nr(t, "class", "svelte-1rt0kpf");
    },
    m(o, s) {
      le(o, t, s), e[8](t), le(o, r, s), a && a.m(o, s), le(o, n, s), i = !0;
    },
    p(o, [s]) {
      /*$$slots*/
      o[4].default ? a ? (a.p(o, s), s & /*$$slots*/
      16 && ue(a, 1)) : (a = St(o), a.c(), ue(a, 1), a.m(n.parentNode, n)) : a && (An(), Xe(a, 1, 1, () => {
        a = null;
      }), Pn());
    },
    i(o) {
      i || (ue(a), i = !0);
    },
    o(o) {
      Xe(a), i = !1;
    },
    d(o) {
      o && (F(t), F(r), F(n)), e[8](null), a && a.d(o);
    }
  };
}
function wt(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function Un(e, t, r) {
  let n, i, {
    $$slots: a = {},
    $$scope: o
  } = t;
  const s = wn(a);
  let {
    svelteInit: u
  } = t;
  const h = L(wt(t)), l = L();
  xt(e, l, (_) => r(0, n = _));
  const c = L();
  xt(e, c, (_) => r(1, i = _));
  const f = [], m = Mn("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: P,
    subSlotIndex: b
  } = qr() || {}, x = u({
    parent: m,
    props: h,
    target: l,
    slot: c,
    slotKey: E,
    slotIndex: P,
    subSlotIndex: b,
    onDestroy(_) {
      f.push(_);
    }
  });
  jn("$$ms-gr-react-wrapper", x), Rn(() => {
    h.set(wt(t));
  }), Ln(() => {
    f.forEach((_) => _());
  });
  function w(_) {
    vt[_ ? "unshift" : "push"](() => {
      n = _, l.set(n);
    });
  }
  function T(_) {
    vt[_ ? "unshift" : "push"](() => {
      i = _, c.set(i);
    });
  }
  return e.$$set = (_) => {
    r(17, t = gt(gt({}, t), Pt(_))), "svelteInit" in _ && r(5, u = _.svelteInit), "$$scope" in _ && r(6, o = _.$$scope);
  }, t = Pt(t), [n, i, l, c, s, u, o, a, w, T];
}
class Fn extends En {
  constructor(t) {
    super(), Cn(this, t, Un, Dn, In, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Po
} = window.__gradio__svelte__internal, Tt = window.ms_globals.rerender, Ne = window.ms_globals.tree;
function kn(e, t = {}) {
  function r(n) {
    const i = L(), a = new Fn({
      ...n,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, u = o.parent ?? Ne;
          return u.nodes = [...u.nodes, s], Tt({
            createPortal: $e,
            node: Ne
          }), o.onDestroy(() => {
            u.nodes = u.nodes.filter((h) => h.svelteInstance !== i), Tt({
              createPortal: $e,
              node: Ne
            });
          }), s;
        },
        ...n.props
      }
    });
    return i.set(a), a;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const Gn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function zn(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const n = e[r];
    return t[r] = $n(r, n), t;
  }, {}) : {};
}
function $n(e, t) {
  return typeof t == "number" && !Gn.includes(e) ? t + "px" : t;
}
function We(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const i = N.Children.toArray(e._reactElement.props.children).map((a) => {
      if (N.isValidElement(a) && a.props.__slot__) {
        const {
          portals: o,
          clonedElement: s
        } = We(a.props.el);
        return N.cloneElement(a, {
          ...a.props,
          el: s,
          children: [...N.Children.toArray(a.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push($e(N.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: o,
      type: s,
      useCapture: u
    }) => {
      r.addEventListener(s, o, u);
    });
  });
  const n = Array.from(e.childNodes);
  for (let i = 0; i < n.length; i++) {
    const a = n[i];
    if (a.nodeType === 1) {
      const {
        clonedElement: o,
        portals: s
      } = We(a);
      t.push(...s), r.appendChild(o);
    } else a.nodeType === 3 && r.appendChild(a.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Vn(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Ze = Vr(({
  slot: e,
  clone: t,
  className: r,
  style: n,
  observeAttributes: i
}, a) => {
  const o = Xr(), [s, u] = Zt([]), {
    forceClone: h
  } = Jr(), l = h ? !0 : t;
  return Yt(() => {
    var P;
    if (!o.current || !e)
      return;
    let c = e;
    function f() {
      let b = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (b = c.children[0], b.tagName.toLowerCase() === "react-portal-target" && b.children[0] && (b = b.children[0])), Vn(a, b), r && b.classList.add(...r.split(" ")), n) {
        const x = zn(n);
        Object.keys(x).forEach((w) => {
          b.style[w] = x[w];
        });
      }
    }
    let m = null, E = null;
    if (l && window.MutationObserver) {
      let b = function() {
        var _, S, g;
        (_ = o.current) != null && _.contains(c) && ((S = o.current) == null || S.removeChild(c));
        const {
          portals: w,
          clonedElement: T
        } = We(e);
        c = T, u(w), c.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          f();
        }, 50), (g = o.current) == null || g.appendChild(c);
      };
      b();
      const x = pn(() => {
        b(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      m = new window.MutationObserver(x), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", f(), (P = o.current) == null || P.appendChild(c);
    return () => {
      var b, x;
      c.style.display = "", (b = o.current) != null && b.contains(c) && ((x = o.current) == null || x.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, l, r, n, a, i, h]), N.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...s);
});
function Xn(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Wn(e, t = !1) {
  try {
    if (Kr(e))
      return e;
    if (t && !Xn(e))
      return;
    if (typeof e == "string") {
      let r = e.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Re(e, t) {
  return Wr(() => Wn(e, t), [e, t]);
}
const Zn = ({
  children: e,
  ...t
}) => /* @__PURE__ */ I.jsx(I.Fragment, {
  children: e(t)
});
function Yn(e) {
  return N.createElement(Zn, {
    children: e
  });
}
function Ht(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? Yn((r) => /* @__PURE__ */ I.jsx(en, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ I.jsx(Ze, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ I.jsx(Ze, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function qn({
  key: e,
  slots: t,
  targets: r
}, n) {
  return t[e] ? (...i) => r ? r.map((a, o) => /* @__PURE__ */ I.jsx(N.Fragment, {
    children: Ht(a, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ I.jsx(I.Fragment, {
    children: Ht(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
var ir = Symbol.for("immer-nothing"), Ot = Symbol.for("immer-draftable"), C = Symbol.for("immer-state");
function B(e, ...t) {
  throw new Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var k = Object.getPrototypeOf;
function G(e) {
  return !!e && !!e[C];
}
function j(e) {
  var t;
  return e ? ar(e) || Array.isArray(e) || !!e[Ot] || !!((t = e.constructor) != null && t[Ot]) || te(e) || ge(e) : !1;
}
var Kn = Object.prototype.constructor.toString();
function ar(e) {
  if (!e || typeof e != "object") return !1;
  const t = k(e);
  if (t === null)
    return !0;
  const r = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
  return r === Object ? !0 : typeof r == "function" && Function.toString.call(r) === Kn;
}
function fe(e, t) {
  be(e) === 0 ? Reflect.ownKeys(e).forEach((r) => {
    t(r, e[r], e);
  }) : e.forEach((r, n) => t(n, r, e));
}
function be(e) {
  const t = e[C];
  return t ? t.type_ : Array.isArray(e) ? 1 : te(e) ? 2 : ge(e) ? 3 : 0;
}
function Ye(e, t) {
  return be(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function or(e, t, r) {
  const n = be(e);
  n === 2 ? e.set(t, r) : n === 3 ? e.add(r) : e[t] = r;
}
function Qn(e, t) {
  return e === t ? e !== 0 || 1 / e === 1 / t : e !== e && t !== t;
}
function te(e) {
  return e instanceof Map;
}
function ge(e) {
  return e instanceof Set;
}
function M(e) {
  return e.copy_ || e.base_;
}
function qe(e, t) {
  if (te(e))
    return new Map(e);
  if (ge(e))
    return new Set(e);
  if (Array.isArray(e)) return Array.prototype.slice.call(e);
  const r = ar(e);
  if (t === !0 || t === "class_only" && !r) {
    const n = Object.getOwnPropertyDescriptors(e);
    delete n[C];
    let i = Reflect.ownKeys(n);
    for (let a = 0; a < i.length; a++) {
      const o = i[a], s = n[o];
      s.writable === !1 && (s.writable = !0, s.configurable = !0), (s.get || s.set) && (n[o] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: s.enumerable,
        value: e[o]
      });
    }
    return Object.create(k(e), n);
  } else {
    const n = k(e);
    if (n !== null && r)
      return {
        ...e
      };
    const i = Object.create(n);
    return Object.assign(i, e);
  }
}
function ct(e, t = !1) {
  return ve(e) || G(e) || !j(e) || (be(e) > 1 && Object.defineProperties(e, {
    set: {
      value: oe
    },
    add: {
      value: oe
    },
    clear: {
      value: oe
    },
    delete: {
      value: oe
    }
  }), Object.freeze(e), t && Object.values(e).forEach((r) => ct(r, !0))), e;
}
function oe() {
  B(2);
}
function ve(e) {
  return Object.isFrozen(e);
}
var Jn = {};
function D(e) {
  const t = Jn[e];
  return t || B(0, e), t;
}
var K;
function sr() {
  return K;
}
function ei(e, t) {
  return {
    drafts_: [],
    parent_: e,
    immer_: t,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function At(e, t) {
  t && (D("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function Ke(e) {
  Qe(e), e.drafts_.forEach(ti), e.drafts_ = null;
}
function Qe(e) {
  e === K && (K = e.parent_);
}
function Ct(e) {
  return K = ei(K, e);
}
function ti(e) {
  const t = e[C];
  t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function It(e, t) {
  t.unfinalizedDrafts_ = t.drafts_.length;
  const r = t.drafts_[0];
  return e !== void 0 && e !== r ? (r[C].modified_ && (Ke(t), B(4)), j(e) && (e = me(t, e), t.parent_ || de(t, e)), t.patches_ && D("Patches").generateReplacementPatches_(r[C].base_, e, t.patches_, t.inversePatches_)) : e = me(t, r, []), Ke(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e !== ir ? e : void 0;
}
function me(e, t, r) {
  if (ve(t)) return t;
  const n = t[C];
  if (!n)
    return fe(t, (i, a) => Bt(e, n, t, i, a, r)), t;
  if (n.scope_ !== e) return t;
  if (!n.modified_)
    return de(e, n.base_, !0), n.base_;
  if (!n.finalized_) {
    n.finalized_ = !0, n.scope_.unfinalizedDrafts_--;
    const i = n.copy_;
    let a = i, o = !1;
    n.type_ === 3 && (a = new Set(i), i.clear(), o = !0), fe(a, (s, u) => Bt(e, n, i, s, u, r, o)), de(e, i, !1), r && e.patches_ && D("Patches").generatePatches_(n, r, e.patches_, e.inversePatches_);
  }
  return n.copy_;
}
function Bt(e, t, r, n, i, a, o) {
  if (G(i)) {
    const s = a && t && t.type_ !== 3 && // Set objects are atomic since they have no keys.
    !Ye(t.assigned_, n) ? a.concat(n) : void 0, u = me(e, i, s);
    if (or(r, n, u), G(u))
      e.canAutoFreeze_ = !1;
    else return;
  } else o && r.add(i);
  if (j(i) && !ve(i)) {
    if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1)
      return;
    me(e, i), (!t || !t.scope_.parent_) && typeof n != "symbol" && (te(r) ? r.has(n) : Object.prototype.propertyIsEnumerable.call(r, n)) && de(e, i);
  }
}
function de(e, t, r = !1) {
  !e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && ct(t, r);
}
function ri(e, t) {
  const r = Array.isArray(e), n = {
    type_: r ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: t ? t.scope_ : sr(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: t,
    // The base state.
    base_: e,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let i = n, a = ft;
  r && (i = [n], a = Q);
  const {
    revoke: o,
    proxy: s
  } = Proxy.revocable(i, a);
  return n.draft_ = s, n.revoke_ = o, s;
}
var ft = {
  get(e, t) {
    if (t === C) return e;
    const r = M(e);
    if (!Ye(r, t))
      return ni(e, r, t);
    const n = r[t];
    return e.finalized_ || !j(n) ? n : n === Me(e.base_, t) ? (Le(e), e.copy_[t] = et(n, e)) : n;
  },
  has(e, t) {
    return t in M(e);
  },
  ownKeys(e) {
    return Reflect.ownKeys(M(e));
  },
  set(e, t, r) {
    const n = lr(M(e), t);
    if (n != null && n.set)
      return n.set.call(e.draft_, r), !0;
    if (!e.modified_) {
      const i = Me(M(e), t), a = i == null ? void 0 : i[C];
      if (a && a.base_ === r)
        return e.copy_[t] = r, e.assigned_[t] = !1, !0;
      if (Qn(r, i) && (r !== void 0 || Ye(e.base_, t))) return !0;
      Le(e), Je(e);
    }
    return e.copy_[t] === r && // special case: handle new props with value 'undefined'
    (r !== void 0 || t in e.copy_) || // special case: NaN
    Number.isNaN(r) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = r, e.assigned_[t] = !0), !0;
  },
  deleteProperty(e, t) {
    return Me(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, Le(e), Je(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(e, t) {
    const r = M(e), n = Reflect.getOwnPropertyDescriptor(r, t);
    return n && {
      writable: !0,
      configurable: e.type_ !== 1 || t !== "length",
      enumerable: n.enumerable,
      value: r[t]
    };
  },
  defineProperty() {
    B(11);
  },
  getPrototypeOf(e) {
    return k(e.base_);
  },
  setPrototypeOf() {
    B(12);
  }
}, Q = {};
fe(ft, (e, t) => {
  Q[e] = function() {
    return arguments[0] = arguments[0][0], t.apply(this, arguments);
  };
});
Q.deleteProperty = function(e, t) {
  return Q.set.call(this, e, t, void 0);
};
Q.set = function(e, t, r) {
  return ft.set.call(this, e[0], t, r, e[0]);
};
function Me(e, t) {
  const r = e[C];
  return (r ? M(r) : e)[t];
}
function ni(e, t, r) {
  var i;
  const n = lr(t, r);
  return n ? "value" in n ? n.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (i = n.get) == null ? void 0 : i.call(e.draft_)
  ) : void 0;
}
function lr(e, t) {
  if (!(t in e)) return;
  let r = k(e);
  for (; r; ) {
    const n = Object.getOwnPropertyDescriptor(r, t);
    if (n) return n;
    r = k(r);
  }
}
function Je(e) {
  e.modified_ || (e.modified_ = !0, e.parent_ && Je(e.parent_));
}
function Le(e) {
  e.copy_ || (e.copy_ = qe(e.base_, e.scope_.immer_.useStrictShallowCopy_));
}
var ii = class {
  constructor(e) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (t, r, n) => {
      if (typeof t == "function" && typeof r != "function") {
        const a = r;
        r = t;
        const o = this;
        return function(u = a, ...h) {
          return o.produce(u, (l) => r.call(this, l, ...h));
        };
      }
      typeof r != "function" && B(6), n !== void 0 && typeof n != "function" && B(7);
      let i;
      if (j(t)) {
        const a = Ct(this), o = et(t, void 0);
        let s = !0;
        try {
          i = r(o), s = !1;
        } finally {
          s ? Ke(a) : Qe(a);
        }
        return At(a, n), It(i, a);
      } else if (!t || typeof t != "object") {
        if (i = r(t), i === void 0 && (i = t), i === ir && (i = void 0), this.autoFreeze_ && ct(i, !0), n) {
          const a = [], o = [];
          D("Patches").generateReplacementPatches_(t, i, a, o), n(a, o);
        }
        return i;
      } else B(1, t);
    }, this.produceWithPatches = (t, r) => {
      if (typeof t == "function")
        return (o, ...s) => this.produceWithPatches(o, (u) => t(u, ...s));
      let n, i;
      return [this.produce(t, r, (o, s) => {
        n = o, i = s;
      }), n, i];
    }, typeof (e == null ? void 0 : e.autoFreeze) == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof (e == null ? void 0 : e.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy);
  }
  createDraft(e) {
    j(e) || B(8), G(e) && (e = ai(e));
    const t = Ct(this), r = et(e, void 0);
    return r[C].isManual_ = !0, Qe(t), r;
  }
  finishDraft(e, t) {
    const r = e && e[C];
    (!r || !r.isManual_) && B(9);
    const {
      scope_: n
    } = r;
    return At(n, t), It(void 0, n);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(e) {
    this.autoFreeze_ = e;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(e) {
    this.useStrictShallowCopy_ = e;
  }
  applyPatches(e, t) {
    let r;
    for (r = t.length - 1; r >= 0; r--) {
      const i = t[r];
      if (i.path.length === 0 && i.op === "replace") {
        e = i.value;
        break;
      }
    }
    r > -1 && (t = t.slice(r + 1));
    const n = D("Patches").applyPatches_;
    return G(e) ? n(e, t) : this.produce(e, (i) => n(i, t));
  }
};
function et(e, t) {
  const r = te(e) ? D("MapSet").proxyMap_(e, t) : ge(e) ? D("MapSet").proxySet_(e, t) : ri(e, t);
  return (t ? t.scope_ : sr()).drafts_.push(r), r;
}
function ai(e) {
  return G(e) || B(10, e), ur(e);
}
function ur(e) {
  if (!j(e) || ve(e)) return e;
  const t = e[C];
  let r;
  if (t) {
    if (!t.modified_) return t.base_;
    t.finalized_ = !0, r = qe(e, t.scope_.immer_.useStrictShallowCopy_);
  } else
    r = qe(e, !0);
  return fe(r, (n, i) => {
    or(r, n, ur(i));
  }), t && (t.finalized_ = !1), r;
}
var oi = new ii(), si = oi.produce, li = function(t) {
  return ui(t) && !hi(t);
};
function ui(e) {
  return !!e && typeof e == "object";
}
function hi(e) {
  var t = Object.prototype.toString.call(e);
  return t === "[object RegExp]" || t === "[object Date]" || mi(e);
}
var ci = typeof Symbol == "function" && Symbol.for, fi = ci ? Symbol.for("react.element") : 60103;
function mi(e) {
  return e.$$typeof === fi;
}
function di(e) {
  return Array.isArray(e) ? [] : {};
}
function J(e, t) {
  return t.clone !== !1 && t.isMergeableObject(e) ? z(di(e), e, t) : e;
}
function pi(e, t, r) {
  return e.concat(t).map(function(n) {
    return J(n, r);
  });
}
function _i(e, t) {
  if (!t.customMerge)
    return z;
  var r = t.customMerge(e);
  return typeof r == "function" ? r : z;
}
function yi(e) {
  return Object.getOwnPropertySymbols ? Object.getOwnPropertySymbols(e).filter(function(t) {
    return Object.propertyIsEnumerable.call(e, t);
  }) : [];
}
function Nt(e) {
  return Object.keys(e).concat(yi(e));
}
function hr(e, t) {
  try {
    return t in e;
  } catch {
    return !1;
  }
}
function bi(e, t) {
  return hr(e, t) && !(Object.hasOwnProperty.call(e, t) && Object.propertyIsEnumerable.call(e, t));
}
function gi(e, t, r) {
  var n = {};
  return r.isMergeableObject(e) && Nt(e).forEach(function(i) {
    n[i] = J(e[i], r);
  }), Nt(t).forEach(function(i) {
    bi(e, i) || (hr(e, i) && r.isMergeableObject(t[i]) ? n[i] = _i(i, r)(e[i], t[i], r) : n[i] = J(t[i], r));
  }), n;
}
function z(e, t, r) {
  r = r || {}, r.arrayMerge = r.arrayMerge || pi, r.isMergeableObject = r.isMergeableObject || li, r.cloneUnlessOtherwiseSpecified = J;
  var n = Array.isArray(t), i = Array.isArray(e), a = n === i;
  return a ? n ? r.arrayMerge(e, t, r) : gi(e, t, r) : J(t, r);
}
z.all = function(t, r) {
  if (!Array.isArray(t))
    throw new Error("first argument should be an array");
  return t.reduce(function(n, i) {
    return z(n, i, r);
  }, {});
};
var vi = z, xi = vi;
const Ei = /* @__PURE__ */ ht(xi);
var tt = function(e, t) {
  return tt = Object.setPrototypeOf || {
    __proto__: []
  } instanceof Array && function(r, n) {
    r.__proto__ = n;
  } || function(r, n) {
    for (var i in n) Object.prototype.hasOwnProperty.call(n, i) && (r[i] = n[i]);
  }, tt(e, t);
};
function xe(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Class extends value " + String(t) + " is not a constructor or null");
  tt(e, t);
  function r() {
    this.constructor = e;
  }
  e.prototype = t === null ? Object.create(t) : (r.prototype = t.prototype, new r());
}
var y = function() {
  return y = Object.assign || function(t) {
    for (var r, n = 1, i = arguments.length; n < i; n++) {
      r = arguments[n];
      for (var a in r) Object.prototype.hasOwnProperty.call(r, a) && (t[a] = r[a]);
    }
    return t;
  }, y.apply(this, arguments);
};
function Pi(e, t) {
  var r = {};
  for (var n in e) Object.prototype.hasOwnProperty.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, n = Object.getOwnPropertySymbols(e); i < n.length; i++)
    t.indexOf(n[i]) < 0 && Object.prototype.propertyIsEnumerable.call(e, n[i]) && (r[n[i]] = e[n[i]]);
  return r;
}
function je(e, t, r) {
  if (r || arguments.length === 2) for (var n = 0, i = t.length, a; n < i; n++)
    (a || !(n in t)) && (a || (a = Array.prototype.slice.call(t, 0, n)), a[n] = t[n]);
  return e.concat(a || Array.prototype.slice.call(t));
}
function De(e, t) {
  var r = t && t.cache ? t.cache : Ci, n = t && t.serializer ? t.serializer : Oi, i = t && t.strategy ? t.strategy : Ti;
  return i(e, {
    cache: r,
    serializer: n
  });
}
function Si(e) {
  return e == null || typeof e == "number" || typeof e == "boolean";
}
function wi(e, t, r, n) {
  var i = Si(n) ? n : r(n), a = t.get(i);
  return typeof a > "u" && (a = e.call(this, n), t.set(i, a)), a;
}
function cr(e, t, r) {
  var n = Array.prototype.slice.call(arguments, 3), i = r(n), a = t.get(i);
  return typeof a > "u" && (a = e.apply(this, n), t.set(i, a)), a;
}
function fr(e, t, r, n, i) {
  return r.bind(t, e, n, i);
}
function Ti(e, t) {
  var r = e.length === 1 ? wi : cr;
  return fr(e, this, r, t.cache.create(), t.serializer);
}
function Hi(e, t) {
  return fr(e, this, cr, t.cache.create(), t.serializer);
}
var Oi = function() {
  return JSON.stringify(arguments);
}, Ai = (
  /** @class */
  function() {
    function e() {
      this.cache = /* @__PURE__ */ Object.create(null);
    }
    return e.prototype.get = function(t) {
      return this.cache[t];
    }, e.prototype.set = function(t, r) {
      this.cache[t] = r;
    }, e;
  }()
), Ci = {
  create: function() {
    return new Ai();
  }
}, Ue = {
  variadic: Hi
}, d;
(function(e) {
  e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
})(d || (d = {}));
var v;
(function(e) {
  e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
})(v || (v = {}));
var $;
(function(e) {
  e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
})($ || ($ = {}));
function Rt(e) {
  return e.type === v.literal;
}
function Ii(e) {
  return e.type === v.argument;
}
function mr(e) {
  return e.type === v.number;
}
function dr(e) {
  return e.type === v.date;
}
function pr(e) {
  return e.type === v.time;
}
function _r(e) {
  return e.type === v.select;
}
function yr(e) {
  return e.type === v.plural;
}
function Bi(e) {
  return e.type === v.pound;
}
function br(e) {
  return e.type === v.tag;
}
function gr(e) {
  return !!(e && typeof e == "object" && e.type === $.number);
}
function rt(e) {
  return !!(e && typeof e == "object" && e.type === $.dateTime);
}
var vr = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/, Ni = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
function Ri(e) {
  var t = {};
  return e.replace(Ni, function(r) {
    var n = r.length;
    switch (r[0]) {
      case "G":
        t.era = n === 4 ? "long" : n === 5 ? "narrow" : "short";
        break;
      case "y":
        t.year = n === 2 ? "2-digit" : "numeric";
        break;
      case "Y":
      case "u":
      case "U":
      case "r":
        throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");
      case "q":
      case "Q":
        throw new RangeError("`q/Q` (quarter) patterns are not supported");
      case "M":
      case "L":
        t.month = ["numeric", "2-digit", "short", "long", "narrow"][n - 1];
        break;
      case "w":
      case "W":
        throw new RangeError("`w/W` (week) patterns are not supported");
      case "d":
        t.day = ["numeric", "2-digit"][n - 1];
        break;
      case "D":
      case "F":
      case "g":
        throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");
      case "E":
        t.weekday = n === 4 ? "long" : n === 5 ? "narrow" : "short";
        break;
      case "e":
        if (n < 4)
          throw new RangeError("`e..eee` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][n - 4];
        break;
      case "c":
        if (n < 4)
          throw new RangeError("`c..ccc` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][n - 4];
        break;
      case "a":
        t.hour12 = !0;
        break;
      case "b":
      case "B":
        throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");
      case "h":
        t.hourCycle = "h12", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "H":
        t.hourCycle = "h23", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "K":
        t.hourCycle = "h11", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "k":
        t.hourCycle = "h24", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "j":
      case "J":
      case "C":
        throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");
      case "m":
        t.minute = ["numeric", "2-digit"][n - 1];
        break;
      case "s":
        t.second = ["numeric", "2-digit"][n - 1];
        break;
      case "S":
      case "A":
        throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");
      case "z":
        t.timeZoneName = n < 4 ? "short" : "long";
        break;
      case "Z":
      case "O":
      case "v":
      case "V":
      case "X":
      case "x":
        throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead");
    }
    return "";
  }), t;
}
var Mi = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
function Li(e) {
  if (e.length === 0)
    throw new Error("Number skeleton cannot be empty");
  for (var t = e.split(Mi).filter(function(f) {
    return f.length > 0;
  }), r = [], n = 0, i = t; n < i.length; n++) {
    var a = i[n], o = a.split("/");
    if (o.length === 0)
      throw new Error("Invalid number skeleton");
    for (var s = o[0], u = o.slice(1), h = 0, l = u; h < l.length; h++) {
      var c = l[h];
      if (c.length === 0)
        throw new Error("Invalid number skeleton");
    }
    r.push({
      stem: s,
      options: u
    });
  }
  return r;
}
function ji(e) {
  return e.replace(/^(.*?)-/, "");
}
var Mt = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g, xr = /^(@+)?(\+|#+)?[rs]?$/g, Di = /(\*)(0+)|(#+)(0+)|(0+)/g, Er = /^(0+)$/;
function Lt(e) {
  var t = {};
  return e[e.length - 1] === "r" ? t.roundingPriority = "morePrecision" : e[e.length - 1] === "s" && (t.roundingPriority = "lessPrecision"), e.replace(xr, function(r, n, i) {
    return typeof i != "string" ? (t.minimumSignificantDigits = n.length, t.maximumSignificantDigits = n.length) : i === "+" ? t.minimumSignificantDigits = n.length : n[0] === "#" ? t.maximumSignificantDigits = n.length : (t.minimumSignificantDigits = n.length, t.maximumSignificantDigits = n.length + (typeof i == "string" ? i.length : 0)), "";
  }), t;
}
function Pr(e) {
  switch (e) {
    case "sign-auto":
      return {
        signDisplay: "auto"
      };
    case "sign-accounting":
    case "()":
      return {
        currencySign: "accounting"
      };
    case "sign-always":
    case "+!":
      return {
        signDisplay: "always"
      };
    case "sign-accounting-always":
    case "()!":
      return {
        signDisplay: "always",
        currencySign: "accounting"
      };
    case "sign-except-zero":
    case "+?":
      return {
        signDisplay: "exceptZero"
      };
    case "sign-accounting-except-zero":
    case "()?":
      return {
        signDisplay: "exceptZero",
        currencySign: "accounting"
      };
    case "sign-never":
    case "+_":
      return {
        signDisplay: "never"
      };
  }
}
function Ui(e) {
  var t;
  if (e[0] === "E" && e[1] === "E" ? (t = {
    notation: "engineering"
  }, e = e.slice(2)) : e[0] === "E" && (t = {
    notation: "scientific"
  }, e = e.slice(1)), t) {
    var r = e.slice(0, 2);
    if (r === "+!" ? (t.signDisplay = "always", e = e.slice(2)) : r === "+?" && (t.signDisplay = "exceptZero", e = e.slice(2)), !Er.test(e))
      throw new Error("Malformed concise eng/scientific notation");
    t.minimumIntegerDigits = e.length;
  }
  return t;
}
function jt(e) {
  var t = {}, r = Pr(e);
  return r || t;
}
function Fi(e) {
  for (var t = {}, r = 0, n = e; r < n.length; r++) {
    var i = n[r];
    switch (i.stem) {
      case "percent":
      case "%":
        t.style = "percent";
        continue;
      case "%x100":
        t.style = "percent", t.scale = 100;
        continue;
      case "currency":
        t.style = "currency", t.currency = i.options[0];
        continue;
      case "group-off":
      case ",_":
        t.useGrouping = !1;
        continue;
      case "precision-integer":
      case ".":
        t.maximumFractionDigits = 0;
        continue;
      case "measure-unit":
      case "unit":
        t.style = "unit", t.unit = ji(i.options[0]);
        continue;
      case "compact-short":
      case "K":
        t.notation = "compact", t.compactDisplay = "short";
        continue;
      case "compact-long":
      case "KK":
        t.notation = "compact", t.compactDisplay = "long";
        continue;
      case "scientific":
        t = y(y(y({}, t), {
          notation: "scientific"
        }), i.options.reduce(function(u, h) {
          return y(y({}, u), jt(h));
        }, {}));
        continue;
      case "engineering":
        t = y(y(y({}, t), {
          notation: "engineering"
        }), i.options.reduce(function(u, h) {
          return y(y({}, u), jt(h));
        }, {}));
        continue;
      case "notation-simple":
        t.notation = "standard";
        continue;
      case "unit-width-narrow":
        t.currencyDisplay = "narrowSymbol", t.unitDisplay = "narrow";
        continue;
      case "unit-width-short":
        t.currencyDisplay = "code", t.unitDisplay = "short";
        continue;
      case "unit-width-full-name":
        t.currencyDisplay = "name", t.unitDisplay = "long";
        continue;
      case "unit-width-iso-code":
        t.currencyDisplay = "symbol";
        continue;
      case "scale":
        t.scale = parseFloat(i.options[0]);
        continue;
      case "rounding-mode-floor":
        t.roundingMode = "floor";
        continue;
      case "rounding-mode-ceiling":
        t.roundingMode = "ceil";
        continue;
      case "rounding-mode-down":
        t.roundingMode = "trunc";
        continue;
      case "rounding-mode-up":
        t.roundingMode = "expand";
        continue;
      case "rounding-mode-half-even":
        t.roundingMode = "halfEven";
        continue;
      case "rounding-mode-half-down":
        t.roundingMode = "halfTrunc";
        continue;
      case "rounding-mode-half-up":
        t.roundingMode = "halfExpand";
        continue;
      case "integer-width":
        if (i.options.length > 1)
          throw new RangeError("integer-width stems only accept a single optional option");
        i.options[0].replace(Di, function(u, h, l, c, f, m) {
          if (h)
            t.minimumIntegerDigits = l.length;
          else {
            if (c && f)
              throw new Error("We currently do not support maximum integer digits");
            if (m)
              throw new Error("We currently do not support exact integer digits");
          }
          return "";
        });
        continue;
    }
    if (Er.test(i.stem)) {
      t.minimumIntegerDigits = i.stem.length;
      continue;
    }
    if (Mt.test(i.stem)) {
      if (i.options.length > 1)
        throw new RangeError("Fraction-precision stems only accept a single optional option");
      i.stem.replace(Mt, function(u, h, l, c, f, m) {
        return l === "*" ? t.minimumFractionDigits = h.length : c && c[0] === "#" ? t.maximumFractionDigits = c.length : f && m ? (t.minimumFractionDigits = f.length, t.maximumFractionDigits = f.length + m.length) : (t.minimumFractionDigits = h.length, t.maximumFractionDigits = h.length), "";
      });
      var a = i.options[0];
      a === "w" ? t = y(y({}, t), {
        trailingZeroDisplay: "stripIfInteger"
      }) : a && (t = y(y({}, t), Lt(a)));
      continue;
    }
    if (xr.test(i.stem)) {
      t = y(y({}, t), Lt(i.stem));
      continue;
    }
    var o = Pr(i.stem);
    o && (t = y(y({}, t), o));
    var s = Ui(i.stem);
    s && (t = y(y({}, t), s));
  }
  return t;
}
var se = {
  "001": ["H", "h"],
  419: ["h", "H", "hB", "hb"],
  AC: ["H", "h", "hb", "hB"],
  AD: ["H", "hB"],
  AE: ["h", "hB", "hb", "H"],
  AF: ["H", "hb", "hB", "h"],
  AG: ["h", "hb", "H", "hB"],
  AI: ["H", "h", "hb", "hB"],
  AL: ["h", "H", "hB"],
  AM: ["H", "hB"],
  AO: ["H", "hB"],
  AR: ["h", "H", "hB", "hb"],
  AS: ["h", "H"],
  AT: ["H", "hB"],
  AU: ["h", "hb", "H", "hB"],
  AW: ["H", "hB"],
  AX: ["H"],
  AZ: ["H", "hB", "h"],
  BA: ["H", "hB", "h"],
  BB: ["h", "hb", "H", "hB"],
  BD: ["h", "hB", "H"],
  BE: ["H", "hB"],
  BF: ["H", "hB"],
  BG: ["H", "hB", "h"],
  BH: ["h", "hB", "hb", "H"],
  BI: ["H", "h"],
  BJ: ["H", "hB"],
  BL: ["H", "hB"],
  BM: ["h", "hb", "H", "hB"],
  BN: ["hb", "hB", "h", "H"],
  BO: ["h", "H", "hB", "hb"],
  BQ: ["H"],
  BR: ["H", "hB"],
  BS: ["h", "hb", "H", "hB"],
  BT: ["h", "H"],
  BW: ["H", "h", "hb", "hB"],
  BY: ["H", "h"],
  BZ: ["H", "h", "hb", "hB"],
  CA: ["h", "hb", "H", "hB"],
  CC: ["H", "h", "hb", "hB"],
  CD: ["hB", "H"],
  CF: ["H", "h", "hB"],
  CG: ["H", "hB"],
  CH: ["H", "hB", "h"],
  CI: ["H", "hB"],
  CK: ["H", "h", "hb", "hB"],
  CL: ["h", "H", "hB", "hb"],
  CM: ["H", "h", "hB"],
  CN: ["H", "hB", "hb", "h"],
  CO: ["h", "H", "hB", "hb"],
  CP: ["H"],
  CR: ["h", "H", "hB", "hb"],
  CU: ["h", "H", "hB", "hb"],
  CV: ["H", "hB"],
  CW: ["H", "hB"],
  CX: ["H", "h", "hb", "hB"],
  CY: ["h", "H", "hb", "hB"],
  CZ: ["H"],
  DE: ["H", "hB"],
  DG: ["H", "h", "hb", "hB"],
  DJ: ["h", "H"],
  DK: ["H"],
  DM: ["h", "hb", "H", "hB"],
  DO: ["h", "H", "hB", "hb"],
  DZ: ["h", "hB", "hb", "H"],
  EA: ["H", "h", "hB", "hb"],
  EC: ["h", "H", "hB", "hb"],
  EE: ["H", "hB"],
  EG: ["h", "hB", "hb", "H"],
  EH: ["h", "hB", "hb", "H"],
  ER: ["h", "H"],
  ES: ["H", "hB", "h", "hb"],
  ET: ["hB", "hb", "h", "H"],
  FI: ["H"],
  FJ: ["h", "hb", "H", "hB"],
  FK: ["H", "h", "hb", "hB"],
  FM: ["h", "hb", "H", "hB"],
  FO: ["H", "h"],
  FR: ["H", "hB"],
  GA: ["H", "hB"],
  GB: ["H", "h", "hb", "hB"],
  GD: ["h", "hb", "H", "hB"],
  GE: ["H", "hB", "h"],
  GF: ["H", "hB"],
  GG: ["H", "h", "hb", "hB"],
  GH: ["h", "H"],
  GI: ["H", "h", "hb", "hB"],
  GL: ["H", "h"],
  GM: ["h", "hb", "H", "hB"],
  GN: ["H", "hB"],
  GP: ["H", "hB"],
  GQ: ["H", "hB", "h", "hb"],
  GR: ["h", "H", "hb", "hB"],
  GT: ["h", "H", "hB", "hb"],
  GU: ["h", "hb", "H", "hB"],
  GW: ["H", "hB"],
  GY: ["h", "hb", "H", "hB"],
  HK: ["h", "hB", "hb", "H"],
  HN: ["h", "H", "hB", "hb"],
  HR: ["H", "hB"],
  HU: ["H", "h"],
  IC: ["H", "h", "hB", "hb"],
  ID: ["H"],
  IE: ["H", "h", "hb", "hB"],
  IL: ["H", "hB"],
  IM: ["H", "h", "hb", "hB"],
  IN: ["h", "H"],
  IO: ["H", "h", "hb", "hB"],
  IQ: ["h", "hB", "hb", "H"],
  IR: ["hB", "H"],
  IS: ["H"],
  IT: ["H", "hB"],
  JE: ["H", "h", "hb", "hB"],
  JM: ["h", "hb", "H", "hB"],
  JO: ["h", "hB", "hb", "H"],
  JP: ["H", "K", "h"],
  KE: ["hB", "hb", "H", "h"],
  KG: ["H", "h", "hB", "hb"],
  KH: ["hB", "h", "H", "hb"],
  KI: ["h", "hb", "H", "hB"],
  KM: ["H", "h", "hB", "hb"],
  KN: ["h", "hb", "H", "hB"],
  KP: ["h", "H", "hB", "hb"],
  KR: ["h", "H", "hB", "hb"],
  KW: ["h", "hB", "hb", "H"],
  KY: ["h", "hb", "H", "hB"],
  KZ: ["H", "hB"],
  LA: ["H", "hb", "hB", "h"],
  LB: ["h", "hB", "hb", "H"],
  LC: ["h", "hb", "H", "hB"],
  LI: ["H", "hB", "h"],
  LK: ["H", "h", "hB", "hb"],
  LR: ["h", "hb", "H", "hB"],
  LS: ["h", "H"],
  LT: ["H", "h", "hb", "hB"],
  LU: ["H", "h", "hB"],
  LV: ["H", "hB", "hb", "h"],
  LY: ["h", "hB", "hb", "H"],
  MA: ["H", "h", "hB", "hb"],
  MC: ["H", "hB"],
  MD: ["H", "hB"],
  ME: ["H", "hB", "h"],
  MF: ["H", "hB"],
  MG: ["H", "h"],
  MH: ["h", "hb", "H", "hB"],
  MK: ["H", "h", "hb", "hB"],
  ML: ["H"],
  MM: ["hB", "hb", "H", "h"],
  MN: ["H", "h", "hb", "hB"],
  MO: ["h", "hB", "hb", "H"],
  MP: ["h", "hb", "H", "hB"],
  MQ: ["H", "hB"],
  MR: ["h", "hB", "hb", "H"],
  MS: ["H", "h", "hb", "hB"],
  MT: ["H", "h"],
  MU: ["H", "h"],
  MV: ["H", "h"],
  MW: ["h", "hb", "H", "hB"],
  MX: ["h", "H", "hB", "hb"],
  MY: ["hb", "hB", "h", "H"],
  MZ: ["H", "hB"],
  NA: ["h", "H", "hB", "hb"],
  NC: ["H", "hB"],
  NE: ["H"],
  NF: ["H", "h", "hb", "hB"],
  NG: ["H", "h", "hb", "hB"],
  NI: ["h", "H", "hB", "hb"],
  NL: ["H", "hB"],
  NO: ["H", "h"],
  NP: ["H", "h", "hB"],
  NR: ["H", "h", "hb", "hB"],
  NU: ["H", "h", "hb", "hB"],
  NZ: ["h", "hb", "H", "hB"],
  OM: ["h", "hB", "hb", "H"],
  PA: ["h", "H", "hB", "hb"],
  PE: ["h", "H", "hB", "hb"],
  PF: ["H", "h", "hB"],
  PG: ["h", "H"],
  PH: ["h", "hB", "hb", "H"],
  PK: ["h", "hB", "H"],
  PL: ["H", "h"],
  PM: ["H", "hB"],
  PN: ["H", "h", "hb", "hB"],
  PR: ["h", "H", "hB", "hb"],
  PS: ["h", "hB", "hb", "H"],
  PT: ["H", "hB"],
  PW: ["h", "H"],
  PY: ["h", "H", "hB", "hb"],
  QA: ["h", "hB", "hb", "H"],
  RE: ["H", "hB"],
  RO: ["H", "hB"],
  RS: ["H", "hB", "h"],
  RU: ["H"],
  RW: ["H", "h"],
  SA: ["h", "hB", "hb", "H"],
  SB: ["h", "hb", "H", "hB"],
  SC: ["H", "h", "hB"],
  SD: ["h", "hB", "hb", "H"],
  SE: ["H"],
  SG: ["h", "hb", "H", "hB"],
  SH: ["H", "h", "hb", "hB"],
  SI: ["H", "hB"],
  SJ: ["H"],
  SK: ["H"],
  SL: ["h", "hb", "H", "hB"],
  SM: ["H", "h", "hB"],
  SN: ["H", "h", "hB"],
  SO: ["h", "H"],
  SR: ["H", "hB"],
  SS: ["h", "hb", "H", "hB"],
  ST: ["H", "hB"],
  SV: ["h", "H", "hB", "hb"],
  SX: ["H", "h", "hb", "hB"],
  SY: ["h", "hB", "hb", "H"],
  SZ: ["h", "hb", "H", "hB"],
  TA: ["H", "h", "hb", "hB"],
  TC: ["h", "hb", "H", "hB"],
  TD: ["h", "H", "hB"],
  TF: ["H", "h", "hB"],
  TG: ["H", "hB"],
  TH: ["H", "h"],
  TJ: ["H", "h"],
  TL: ["H", "hB", "hb", "h"],
  TM: ["H", "h"],
  TN: ["h", "hB", "hb", "H"],
  TO: ["h", "H"],
  TR: ["H", "hB"],
  TT: ["h", "hb", "H", "hB"],
  TW: ["hB", "hb", "h", "H"],
  TZ: ["hB", "hb", "H", "h"],
  UA: ["H", "hB", "h"],
  UG: ["hB", "hb", "H", "h"],
  UM: ["h", "hb", "H", "hB"],
  US: ["h", "hb", "H", "hB"],
  UY: ["h", "H", "hB", "hb"],
  UZ: ["H", "hB", "h"],
  VA: ["H", "h", "hB"],
  VC: ["h", "hb", "H", "hB"],
  VE: ["h", "H", "hB", "hb"],
  VG: ["h", "hb", "H", "hB"],
  VI: ["h", "hb", "H", "hB"],
  VN: ["H", "h"],
  VU: ["h", "H"],
  WF: ["H", "hB"],
  WS: ["h", "H"],
  XK: ["H", "hB", "h"],
  YE: ["h", "hB", "hb", "H"],
  YT: ["H", "hB"],
  ZA: ["H", "h", "hb", "hB"],
  ZM: ["h", "hb", "H", "hB"],
  ZW: ["H", "h"],
  "af-ZA": ["H", "h", "hB", "hb"],
  "ar-001": ["h", "hB", "hb", "H"],
  "ca-ES": ["H", "h", "hB"],
  "en-001": ["h", "hb", "H", "hB"],
  "en-HK": ["h", "hb", "H", "hB"],
  "en-IL": ["H", "h", "hb", "hB"],
  "en-MY": ["h", "hb", "H", "hB"],
  "es-BR": ["H", "h", "hB", "hb"],
  "es-ES": ["H", "h", "hB", "hb"],
  "es-GQ": ["H", "h", "hB", "hb"],
  "fr-CA": ["H", "h", "hB"],
  "gl-ES": ["H", "h", "hB"],
  "gu-IN": ["hB", "hb", "h", "H"],
  "hi-IN": ["hB", "h", "H"],
  "it-CH": ["H", "h", "hB"],
  "it-IT": ["H", "h", "hB"],
  "kn-IN": ["hB", "h", "H"],
  "ml-IN": ["hB", "h", "H"],
  "mr-IN": ["hB", "hb", "h", "H"],
  "pa-IN": ["hB", "hb", "h", "H"],
  "ta-IN": ["hB", "h", "hb", "H"],
  "te-IN": ["hB", "h", "H"],
  "zu-ZA": ["H", "hB", "hb", "h"]
};
function ki(e, t) {
  for (var r = "", n = 0; n < e.length; n++) {
    var i = e.charAt(n);
    if (i === "j") {
      for (var a = 0; n + 1 < e.length && e.charAt(n + 1) === i; )
        a++, n++;
      var o = 1 + (a & 1), s = a < 2 ? 1 : 3 + (a >> 1), u = "a", h = Gi(t);
      for ((h == "H" || h == "k") && (s = 0); s-- > 0; )
        r += u;
      for (; o-- > 0; )
        r = h + r;
    } else i === "J" ? r += "H" : r += i;
  }
  return r;
}
function Gi(e) {
  var t = e.hourCycle;
  if (t === void 0 && // @ts-ignore hourCycle(s) is not identified yet
  e.hourCycles && // @ts-ignore
  e.hourCycles.length && (t = e.hourCycles[0]), t)
    switch (t) {
      case "h24":
        return "k";
      case "h23":
        return "H";
      case "h12":
        return "h";
      case "h11":
        return "K";
      default:
        throw new Error("Invalid hourCycle");
    }
  var r = e.language, n;
  r !== "root" && (n = e.maximize().region);
  var i = se[n || ""] || se[r || ""] || se["".concat(r, "-001")] || se["001"];
  return i[0];
}
var Fe, zi = new RegExp("^".concat(vr.source, "*")), $i = new RegExp("".concat(vr.source, "*$"));
function p(e, t) {
  return {
    start: e,
    end: t
  };
}
var Vi = !!String.prototype.startsWith && "_a".startsWith("a", 1), Xi = !!String.fromCodePoint, Wi = !!Object.fromEntries, Zi = !!String.prototype.codePointAt, Yi = !!String.prototype.trimStart, qi = !!String.prototype.trimEnd, Ki = !!Number.isSafeInteger, Qi = Ki ? Number.isSafeInteger : function(e) {
  return typeof e == "number" && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
}, nt = !0;
try {
  var Ji = wr("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  nt = ((Fe = Ji.exec("a")) === null || Fe === void 0 ? void 0 : Fe[0]) === "a";
} catch {
  nt = !1;
}
var Dt = Vi ? (
  // Native
  function(t, r, n) {
    return t.startsWith(r, n);
  }
) : (
  // For IE11
  function(t, r, n) {
    return t.slice(n, n + r.length) === r;
  }
), it = Xi ? String.fromCodePoint : (
  // IE11
  function() {
    for (var t = [], r = 0; r < arguments.length; r++)
      t[r] = arguments[r];
    for (var n = "", i = t.length, a = 0, o; i > a; ) {
      if (o = t[a++], o > 1114111) throw RangeError(o + " is not a valid code point");
      n += o < 65536 ? String.fromCharCode(o) : String.fromCharCode(((o -= 65536) >> 10) + 55296, o % 1024 + 56320);
    }
    return n;
  }
), Ut = (
  // native
  Wi ? Object.fromEntries : (
    // Ponyfill
    function(t) {
      for (var r = {}, n = 0, i = t; n < i.length; n++) {
        var a = i[n], o = a[0], s = a[1];
        r[o] = s;
      }
      return r;
    }
  )
), Sr = Zi ? (
  // Native
  function(t, r) {
    return t.codePointAt(r);
  }
) : (
  // IE 11
  function(t, r) {
    var n = t.length;
    if (!(r < 0 || r >= n)) {
      var i = t.charCodeAt(r), a;
      return i < 55296 || i > 56319 || r + 1 === n || (a = t.charCodeAt(r + 1)) < 56320 || a > 57343 ? i : (i - 55296 << 10) + (a - 56320) + 65536;
    }
  }
), ea = Yi ? (
  // Native
  function(t) {
    return t.trimStart();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace(zi, "");
  }
), ta = qi ? (
  // Native
  function(t) {
    return t.trimEnd();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace($i, "");
  }
);
function wr(e, t) {
  return new RegExp(e, t);
}
var at;
if (nt) {
  var Ft = wr("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  at = function(t, r) {
    var n;
    Ft.lastIndex = r;
    var i = Ft.exec(t);
    return (n = i[1]) !== null && n !== void 0 ? n : "";
  };
} else
  at = function(t, r) {
    for (var n = []; ; ) {
      var i = Sr(t, r);
      if (i === void 0 || Tr(i) || aa(i))
        break;
      n.push(i), r += i >= 65536 ? 2 : 1;
    }
    return it.apply(void 0, n);
  };
var ra = (
  /** @class */
  function() {
    function e(t, r) {
      r === void 0 && (r = {}), this.message = t, this.position = {
        offset: 0,
        line: 1,
        column: 1
      }, this.ignoreTag = !!r.ignoreTag, this.locale = r.locale, this.requiresOtherClause = !!r.requiresOtherClause, this.shouldParseSkeletons = !!r.shouldParseSkeletons;
    }
    return e.prototype.parse = function() {
      if (this.offset() !== 0)
        throw Error("parser can only be used once");
      return this.parseMessage(0, "", !1);
    }, e.prototype.parseMessage = function(t, r, n) {
      for (var i = []; !this.isEOF(); ) {
        var a = this.char();
        if (a === 123) {
          var o = this.parseArgument(t, n);
          if (o.err)
            return o;
          i.push(o.val);
        } else {
          if (a === 125 && t > 0)
            break;
          if (a === 35 && (r === "plural" || r === "selectordinal")) {
            var s = this.clonePosition();
            this.bump(), i.push({
              type: v.pound,
              location: p(s, this.clonePosition())
            });
          } else if (a === 60 && !this.ignoreTag && this.peek() === 47) {
            if (n)
              break;
            return this.error(d.UNMATCHED_CLOSING_TAG, p(this.clonePosition(), this.clonePosition()));
          } else if (a === 60 && !this.ignoreTag && ot(this.peek() || 0)) {
            var o = this.parseTag(t, r);
            if (o.err)
              return o;
            i.push(o.val);
          } else {
            var o = this.parseLiteral(t, r);
            if (o.err)
              return o;
            i.push(o.val);
          }
        }
      }
      return {
        val: i,
        err: null
      };
    }, e.prototype.parseTag = function(t, r) {
      var n = this.clonePosition();
      this.bump();
      var i = this.parseTagName();
      if (this.bumpSpace(), this.bumpIf("/>"))
        return {
          val: {
            type: v.literal,
            value: "<".concat(i, "/>"),
            location: p(n, this.clonePosition())
          },
          err: null
        };
      if (this.bumpIf(">")) {
        var a = this.parseMessage(t + 1, r, !0);
        if (a.err)
          return a;
        var o = a.val, s = this.clonePosition();
        if (this.bumpIf("</")) {
          if (this.isEOF() || !ot(this.char()))
            return this.error(d.INVALID_TAG, p(s, this.clonePosition()));
          var u = this.clonePosition(), h = this.parseTagName();
          return i !== h ? this.error(d.UNMATCHED_CLOSING_TAG, p(u, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
            val: {
              type: v.tag,
              value: i,
              children: o,
              location: p(n, this.clonePosition())
            },
            err: null
          } : this.error(d.INVALID_TAG, p(s, this.clonePosition())));
        } else
          return this.error(d.UNCLOSED_TAG, p(n, this.clonePosition()));
      } else
        return this.error(d.INVALID_TAG, p(n, this.clonePosition()));
    }, e.prototype.parseTagName = function() {
      var t = this.offset();
      for (this.bump(); !this.isEOF() && ia(this.char()); )
        this.bump();
      return this.message.slice(t, this.offset());
    }, e.prototype.parseLiteral = function(t, r) {
      for (var n = this.clonePosition(), i = ""; ; ) {
        var a = this.tryParseQuote(r);
        if (a) {
          i += a;
          continue;
        }
        var o = this.tryParseUnquoted(t, r);
        if (o) {
          i += o;
          continue;
        }
        var s = this.tryParseLeftAngleBracket();
        if (s) {
          i += s;
          continue;
        }
        break;
      }
      var u = p(n, this.clonePosition());
      return {
        val: {
          type: v.literal,
          value: i,
          location: u
        },
        err: null
      };
    }, e.prototype.tryParseLeftAngleBracket = function() {
      return !this.isEOF() && this.char() === 60 && (this.ignoreTag || // If at the opening tag or closing tag position, bail.
      !na(this.peek() || 0)) ? (this.bump(), "<") : null;
    }, e.prototype.tryParseQuote = function(t) {
      if (this.isEOF() || this.char() !== 39)
        return null;
      switch (this.peek()) {
        case 39:
          return this.bump(), this.bump(), "'";
        case 123:
        case 60:
        case 62:
        case 125:
          break;
        case 35:
          if (t === "plural" || t === "selectordinal")
            break;
          return null;
        default:
          return null;
      }
      this.bump();
      var r = [this.char()];
      for (this.bump(); !this.isEOF(); ) {
        var n = this.char();
        if (n === 39)
          if (this.peek() === 39)
            r.push(39), this.bump();
          else {
            this.bump();
            break;
          }
        else
          r.push(n);
        this.bump();
      }
      return it.apply(void 0, r);
    }, e.prototype.tryParseUnquoted = function(t, r) {
      if (this.isEOF())
        return null;
      var n = this.char();
      return n === 60 || n === 123 || n === 35 && (r === "plural" || r === "selectordinal") || n === 125 && t > 0 ? null : (this.bump(), it(n));
    }, e.prototype.parseArgument = function(t, r) {
      var n = this.clonePosition();
      if (this.bump(), this.bumpSpace(), this.isEOF())
        return this.error(d.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition()));
      if (this.char() === 125)
        return this.bump(), this.error(d.EMPTY_ARGUMENT, p(n, this.clonePosition()));
      var i = this.parseIdentifierIfPossible().value;
      if (!i)
        return this.error(d.MALFORMED_ARGUMENT, p(n, this.clonePosition()));
      if (this.bumpSpace(), this.isEOF())
        return this.error(d.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition()));
      switch (this.char()) {
        case 125:
          return this.bump(), {
            val: {
              type: v.argument,
              // value does not include the opening and closing braces.
              value: i,
              location: p(n, this.clonePosition())
            },
            err: null
          };
        case 44:
          return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(d.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition())) : this.parseArgumentOptions(t, r, i, n);
        default:
          return this.error(d.MALFORMED_ARGUMENT, p(n, this.clonePosition()));
      }
    }, e.prototype.parseIdentifierIfPossible = function() {
      var t = this.clonePosition(), r = this.offset(), n = at(this.message, r), i = r + n.length;
      this.bumpTo(i);
      var a = this.clonePosition(), o = p(t, a);
      return {
        value: n,
        location: o
      };
    }, e.prototype.parseArgumentOptions = function(t, r, n, i) {
      var a, o = this.clonePosition(), s = this.parseIdentifierIfPossible().value, u = this.clonePosition();
      switch (s) {
        case "":
          return this.error(d.EXPECT_ARGUMENT_TYPE, p(o, u));
        case "number":
        case "date":
        case "time": {
          this.bumpSpace();
          var h = null;
          if (this.bumpIf(",")) {
            this.bumpSpace();
            var l = this.clonePosition(), c = this.parseSimpleArgStyleIfPossible();
            if (c.err)
              return c;
            var f = ta(c.val);
            if (f.length === 0)
              return this.error(d.EXPECT_ARGUMENT_STYLE, p(this.clonePosition(), this.clonePosition()));
            var m = p(l, this.clonePosition());
            h = {
              style: f,
              styleLocation: m
            };
          }
          var E = this.tryParseArgumentClose(i);
          if (E.err)
            return E;
          var P = p(i, this.clonePosition());
          if (h && Dt(h == null ? void 0 : h.style, "::", 0)) {
            var b = ea(h.style.slice(2));
            if (s === "number") {
              var c = this.parseNumberSkeletonFromString(b, h.styleLocation);
              return c.err ? c : {
                val: {
                  type: v.number,
                  value: n,
                  location: P,
                  style: c.val
                },
                err: null
              };
            } else {
              if (b.length === 0)
                return this.error(d.EXPECT_DATE_TIME_SKELETON, P);
              var x = b;
              this.locale && (x = ki(b, this.locale));
              var f = {
                type: $.dateTime,
                pattern: x,
                location: h.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? Ri(x) : {}
              }, w = s === "date" ? v.date : v.time;
              return {
                val: {
                  type: w,
                  value: n,
                  location: P,
                  style: f
                },
                err: null
              };
            }
          }
          return {
            val: {
              type: s === "number" ? v.number : s === "date" ? v.date : v.time,
              value: n,
              location: P,
              style: (a = h == null ? void 0 : h.style) !== null && a !== void 0 ? a : null
            },
            err: null
          };
        }
        case "plural":
        case "selectordinal":
        case "select": {
          var T = this.clonePosition();
          if (this.bumpSpace(), !this.bumpIf(","))
            return this.error(d.EXPECT_SELECT_ARGUMENT_OPTIONS, p(T, y({}, T)));
          this.bumpSpace();
          var _ = this.parseIdentifierIfPossible(), S = 0;
          if (s !== "select" && _.value === "offset") {
            if (!this.bumpIf(":"))
              return this.error(d.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, p(this.clonePosition(), this.clonePosition()));
            this.bumpSpace();
            var c = this.tryParseDecimalInteger(d.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, d.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE);
            if (c.err)
              return c;
            this.bumpSpace(), _ = this.parseIdentifierIfPossible(), S = c.val;
          }
          var g = this.tryParsePluralOrSelectOptions(t, s, r, _);
          if (g.err)
            return g;
          var E = this.tryParseArgumentClose(i);
          if (E.err)
            return E;
          var O = p(i, this.clonePosition());
          return s === "select" ? {
            val: {
              type: v.select,
              value: n,
              options: Ut(g.val),
              location: O
            },
            err: null
          } : {
            val: {
              type: v.plural,
              value: n,
              options: Ut(g.val),
              offset: S,
              pluralType: s === "plural" ? "cardinal" : "ordinal",
              location: O
            },
            err: null
          };
        }
        default:
          return this.error(d.INVALID_ARGUMENT_TYPE, p(o, u));
      }
    }, e.prototype.tryParseArgumentClose = function(t) {
      return this.isEOF() || this.char() !== 125 ? this.error(d.EXPECT_ARGUMENT_CLOSING_BRACE, p(t, this.clonePosition())) : (this.bump(), {
        val: !0,
        err: null
      });
    }, e.prototype.parseSimpleArgStyleIfPossible = function() {
      for (var t = 0, r = this.clonePosition(); !this.isEOF(); ) {
        var n = this.char();
        switch (n) {
          case 39: {
            this.bump();
            var i = this.clonePosition();
            if (!this.bumpUntil("'"))
              return this.error(d.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, p(i, this.clonePosition()));
            this.bump();
            break;
          }
          case 123: {
            t += 1, this.bump();
            break;
          }
          case 125: {
            if (t > 0)
              t -= 1;
            else
              return {
                val: this.message.slice(r.offset, this.offset()),
                err: null
              };
            break;
          }
          default:
            this.bump();
            break;
        }
      }
      return {
        val: this.message.slice(r.offset, this.offset()),
        err: null
      };
    }, e.prototype.parseNumberSkeletonFromString = function(t, r) {
      var n = [];
      try {
        n = Li(t);
      } catch {
        return this.error(d.INVALID_NUMBER_SKELETON, r);
      }
      return {
        val: {
          type: $.number,
          tokens: n,
          location: r,
          parsedOptions: this.shouldParseSkeletons ? Fi(n) : {}
        },
        err: null
      };
    }, e.prototype.tryParsePluralOrSelectOptions = function(t, r, n, i) {
      for (var a, o = !1, s = [], u = /* @__PURE__ */ new Set(), h = i.value, l = i.location; ; ) {
        if (h.length === 0) {
          var c = this.clonePosition();
          if (r !== "select" && this.bumpIf("=")) {
            var f = this.tryParseDecimalInteger(d.EXPECT_PLURAL_ARGUMENT_SELECTOR, d.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (f.err)
              return f;
            l = p(c, this.clonePosition()), h = this.message.slice(c.offset, this.offset());
          } else
            break;
        }
        if (u.has(h))
          return this.error(r === "select" ? d.DUPLICATE_SELECT_ARGUMENT_SELECTOR : d.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, l);
        h === "other" && (o = !0), this.bumpSpace();
        var m = this.clonePosition();
        if (!this.bumpIf("{"))
          return this.error(r === "select" ? d.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : d.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, p(this.clonePosition(), this.clonePosition()));
        var E = this.parseMessage(t + 1, r, n);
        if (E.err)
          return E;
        var P = this.tryParseArgumentClose(m);
        if (P.err)
          return P;
        s.push([h, {
          value: E.val,
          location: p(m, this.clonePosition())
        }]), u.add(h), this.bumpSpace(), a = this.parseIdentifierIfPossible(), h = a.value, l = a.location;
      }
      return s.length === 0 ? this.error(r === "select" ? d.EXPECT_SELECT_ARGUMENT_SELECTOR : d.EXPECT_PLURAL_ARGUMENT_SELECTOR, p(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !o ? this.error(d.MISSING_OTHER_CLAUSE, p(this.clonePosition(), this.clonePosition())) : {
        val: s,
        err: null
      };
    }, e.prototype.tryParseDecimalInteger = function(t, r) {
      var n = 1, i = this.clonePosition();
      this.bumpIf("+") || this.bumpIf("-") && (n = -1);
      for (var a = !1, o = 0; !this.isEOF(); ) {
        var s = this.char();
        if (s >= 48 && s <= 57)
          a = !0, o = o * 10 + (s - 48), this.bump();
        else
          break;
      }
      var u = p(i, this.clonePosition());
      return a ? (o *= n, Qi(o) ? {
        val: o,
        err: null
      } : this.error(r, u)) : this.error(t, u);
    }, e.prototype.offset = function() {
      return this.position.offset;
    }, e.prototype.isEOF = function() {
      return this.offset() === this.message.length;
    }, e.prototype.clonePosition = function() {
      return {
        offset: this.position.offset,
        line: this.position.line,
        column: this.position.column
      };
    }, e.prototype.char = function() {
      var t = this.position.offset;
      if (t >= this.message.length)
        throw Error("out of bound");
      var r = Sr(this.message, t);
      if (r === void 0)
        throw Error("Offset ".concat(t, " is at invalid UTF-16 code unit boundary"));
      return r;
    }, e.prototype.error = function(t, r) {
      return {
        val: null,
        err: {
          kind: t,
          message: this.message,
          location: r
        }
      };
    }, e.prototype.bump = function() {
      if (!this.isEOF()) {
        var t = this.char();
        t === 10 ? (this.position.line += 1, this.position.column = 1, this.position.offset += 1) : (this.position.column += 1, this.position.offset += t < 65536 ? 1 : 2);
      }
    }, e.prototype.bumpIf = function(t) {
      if (Dt(this.message, t, this.offset())) {
        for (var r = 0; r < t.length; r++)
          this.bump();
        return !0;
      }
      return !1;
    }, e.prototype.bumpUntil = function(t) {
      var r = this.offset(), n = this.message.indexOf(t, r);
      return n >= 0 ? (this.bumpTo(n), !0) : (this.bumpTo(this.message.length), !1);
    }, e.prototype.bumpTo = function(t) {
      if (this.offset() > t)
        throw Error("targetOffset ".concat(t, " must be greater than or equal to the current offset ").concat(this.offset()));
      for (t = Math.min(t, this.message.length); ; ) {
        var r = this.offset();
        if (r === t)
          break;
        if (r > t)
          throw Error("targetOffset ".concat(t, " is at invalid UTF-16 code unit boundary"));
        if (this.bump(), this.isEOF())
          break;
      }
    }, e.prototype.bumpSpace = function() {
      for (; !this.isEOF() && Tr(this.char()); )
        this.bump();
    }, e.prototype.peek = function() {
      if (this.isEOF())
        return null;
      var t = this.char(), r = this.offset(), n = this.message.charCodeAt(r + (t >= 65536 ? 2 : 1));
      return n ?? null;
    }, e;
  }()
);
function ot(e) {
  return e >= 97 && e <= 122 || e >= 65 && e <= 90;
}
function na(e) {
  return ot(e) || e === 47;
}
function ia(e) {
  return e === 45 || e === 46 || e >= 48 && e <= 57 || e === 95 || e >= 97 && e <= 122 || e >= 65 && e <= 90 || e == 183 || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
}
function Tr(e) {
  return e >= 9 && e <= 13 || e === 32 || e === 133 || e >= 8206 && e <= 8207 || e === 8232 || e === 8233;
}
function aa(e) {
  return e >= 33 && e <= 35 || e === 36 || e >= 37 && e <= 39 || e === 40 || e === 41 || e === 42 || e === 43 || e === 44 || e === 45 || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || e === 91 || e === 92 || e === 93 || e === 94 || e === 96 || e === 123 || e === 124 || e === 125 || e === 126 || e === 161 || e >= 162 && e <= 165 || e === 166 || e === 167 || e === 169 || e === 171 || e === 172 || e === 174 || e === 176 || e === 177 || e === 182 || e === 187 || e === 191 || e === 215 || e === 247 || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || e === 8216 || e === 8217 || e === 8218 || e >= 8219 && e <= 8220 || e === 8221 || e === 8222 || e === 8223 || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || e === 8249 || e === 8250 || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || e === 8260 || e === 8261 || e === 8262 || e >= 8263 && e <= 8273 || e === 8274 || e === 8275 || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || e === 8608 || e >= 8609 && e <= 8610 || e === 8611 || e >= 8612 && e <= 8613 || e === 8614 || e >= 8615 && e <= 8621 || e === 8622 || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || e === 8658 || e === 8659 || e === 8660 || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || e === 8968 || e === 8969 || e === 8970 || e === 8971 || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || e === 9001 || e === 9002 || e >= 9003 && e <= 9083 || e === 9084 || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || e === 9655 || e >= 9656 && e <= 9664 || e === 9665 || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || e === 9839 || e >= 9840 && e <= 10087 || e === 10088 || e === 10089 || e === 10090 || e === 10091 || e === 10092 || e === 10093 || e === 10094 || e === 10095 || e === 10096 || e === 10097 || e === 10098 || e === 10099 || e === 10100 || e === 10101 || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || e === 10181 || e === 10182 || e >= 10183 && e <= 10213 || e === 10214 || e === 10215 || e === 10216 || e === 10217 || e === 10218 || e === 10219 || e === 10220 || e === 10221 || e === 10222 || e === 10223 || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || e === 10627 || e === 10628 || e === 10629 || e === 10630 || e === 10631 || e === 10632 || e === 10633 || e === 10634 || e === 10635 || e === 10636 || e === 10637 || e === 10638 || e === 10639 || e === 10640 || e === 10641 || e === 10642 || e === 10643 || e === 10644 || e === 10645 || e === 10646 || e === 10647 || e === 10648 || e >= 10649 && e <= 10711 || e === 10712 || e === 10713 || e === 10714 || e === 10715 || e >= 10716 && e <= 10747 || e === 10748 || e === 10749 || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || e === 11158 || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || e === 11778 || e === 11779 || e === 11780 || e === 11781 || e >= 11782 && e <= 11784 || e === 11785 || e === 11786 || e === 11787 || e === 11788 || e === 11789 || e >= 11790 && e <= 11798 || e === 11799 || e >= 11800 && e <= 11801 || e === 11802 || e === 11803 || e === 11804 || e === 11805 || e >= 11806 && e <= 11807 || e === 11808 || e === 11809 || e === 11810 || e === 11811 || e === 11812 || e === 11813 || e === 11814 || e === 11815 || e === 11816 || e === 11817 || e >= 11818 && e <= 11822 || e === 11823 || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || e === 11840 || e === 11841 || e === 11842 || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || e === 11858 || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || e === 12296 || e === 12297 || e === 12298 || e === 12299 || e === 12300 || e === 12301 || e === 12302 || e === 12303 || e === 12304 || e === 12305 || e >= 12306 && e <= 12307 || e === 12308 || e === 12309 || e === 12310 || e === 12311 || e === 12312 || e === 12313 || e === 12314 || e === 12315 || e === 12316 || e === 12317 || e >= 12318 && e <= 12319 || e === 12320 || e === 12336 || e === 64830 || e === 64831 || e >= 65093 && e <= 65094;
}
function st(e) {
  e.forEach(function(t) {
    if (delete t.location, _r(t) || yr(t))
      for (var r in t.options)
        delete t.options[r].location, st(t.options[r].value);
    else mr(t) && gr(t.style) || (dr(t) || pr(t)) && rt(t.style) ? delete t.style.location : br(t) && st(t.children);
  });
}
function oa(e, t) {
  t === void 0 && (t = {}), t = y({
    shouldParseSkeletons: !0,
    requiresOtherClause: !0
  }, t);
  var r = new ra(e, t).parse();
  if (r.err) {
    var n = SyntaxError(d[r.err.kind]);
    throw n.location = r.err.location, n.originalMessage = r.err.message, n;
  }
  return t != null && t.captureLocation || st(r.val), r.val;
}
var V;
(function(e) {
  e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
})(V || (V = {}));
var Ee = (
  /** @class */
  function(e) {
    xe(t, e);
    function t(r, n, i) {
      var a = e.call(this, r) || this;
      return a.code = n, a.originalMessage = i, a;
    }
    return t.prototype.toString = function() {
      return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
    }, t;
  }(Error)
), kt = (
  /** @class */
  function(e) {
    xe(t, e);
    function t(r, n, i, a) {
      return e.call(this, 'Invalid values for "'.concat(r, '": "').concat(n, '". Options are "').concat(Object.keys(i).join('", "'), '"'), V.INVALID_VALUE, a) || this;
    }
    return t;
  }(Ee)
), sa = (
  /** @class */
  function(e) {
    xe(t, e);
    function t(r, n, i) {
      return e.call(this, 'Value for "'.concat(r, '" must be of type ').concat(n), V.INVALID_VALUE, i) || this;
    }
    return t;
  }(Ee)
), la = (
  /** @class */
  function(e) {
    xe(t, e);
    function t(r, n) {
      return e.call(this, 'The intl string context variable "'.concat(r, '" was not provided to the string "').concat(n, '"'), V.MISSING_VALUE, n) || this;
    }
    return t;
  }(Ee)
), H;
(function(e) {
  e[e.literal = 0] = "literal", e[e.object = 1] = "object";
})(H || (H = {}));
function ua(e) {
  return e.length < 2 ? e : e.reduce(function(t, r) {
    var n = t[t.length - 1];
    return !n || n.type !== H.literal || r.type !== H.literal ? t.push(r) : n.value += r.value, t;
  }, []);
}
function ha(e) {
  return typeof e == "function";
}
function he(e, t, r, n, i, a, o) {
  if (e.length === 1 && Rt(e[0]))
    return [{
      type: H.literal,
      value: e[0].value
    }];
  for (var s = [], u = 0, h = e; u < h.length; u++) {
    var l = h[u];
    if (Rt(l)) {
      s.push({
        type: H.literal,
        value: l.value
      });
      continue;
    }
    if (Bi(l)) {
      typeof a == "number" && s.push({
        type: H.literal,
        value: r.getNumberFormat(t).format(a)
      });
      continue;
    }
    var c = l.value;
    if (!(i && c in i))
      throw new la(c, o);
    var f = i[c];
    if (Ii(l)) {
      (!f || typeof f == "string" || typeof f == "number") && (f = typeof f == "string" || typeof f == "number" ? String(f) : ""), s.push({
        type: typeof f == "string" ? H.literal : H.object,
        value: f
      });
      continue;
    }
    if (dr(l)) {
      var m = typeof l.style == "string" ? n.date[l.style] : rt(l.style) ? l.style.parsedOptions : void 0;
      s.push({
        type: H.literal,
        value: r.getDateTimeFormat(t, m).format(f)
      });
      continue;
    }
    if (pr(l)) {
      var m = typeof l.style == "string" ? n.time[l.style] : rt(l.style) ? l.style.parsedOptions : n.time.medium;
      s.push({
        type: H.literal,
        value: r.getDateTimeFormat(t, m).format(f)
      });
      continue;
    }
    if (mr(l)) {
      var m = typeof l.style == "string" ? n.number[l.style] : gr(l.style) ? l.style.parsedOptions : void 0;
      m && m.scale && (f = f * (m.scale || 1)), s.push({
        type: H.literal,
        value: r.getNumberFormat(t, m).format(f)
      });
      continue;
    }
    if (br(l)) {
      var E = l.children, P = l.value, b = i[P];
      if (!ha(b))
        throw new sa(P, "function", o);
      var x = he(E, t, r, n, i, a), w = b(x.map(function(S) {
        return S.value;
      }));
      Array.isArray(w) || (w = [w]), s.push.apply(s, w.map(function(S) {
        return {
          type: typeof S == "string" ? H.literal : H.object,
          value: S
        };
      }));
    }
    if (_r(l)) {
      var T = l.options[f] || l.options.other;
      if (!T)
        throw new kt(l.value, f, Object.keys(l.options), o);
      s.push.apply(s, he(T.value, t, r, n, i));
      continue;
    }
    if (yr(l)) {
      var T = l.options["=".concat(f)];
      if (!T) {
        if (!Intl.PluralRules)
          throw new Ee(`Intl.PluralRules is not available in this environment.
Try polyfilling it using "@formatjs/intl-pluralrules"
`, V.MISSING_INTL_API, o);
        var _ = r.getPluralRules(t, {
          type: l.pluralType
        }).select(f - (l.offset || 0));
        T = l.options[_] || l.options.other;
      }
      if (!T)
        throw new kt(l.value, f, Object.keys(l.options), o);
      s.push.apply(s, he(T.value, t, r, n, i, f - (l.offset || 0)));
      continue;
    }
  }
  return ua(s);
}
function ca(e, t) {
  return t ? y(y(y({}, e || {}), t || {}), Object.keys(e).reduce(function(r, n) {
    return r[n] = y(y({}, e[n]), t[n] || {}), r;
  }, {})) : e;
}
function fa(e, t) {
  return t ? Object.keys(e).reduce(function(r, n) {
    return r[n] = ca(e[n], t[n]), r;
  }, y({}, e)) : e;
}
function ke(e) {
  return {
    create: function() {
      return {
        get: function(t) {
          return e[t];
        },
        set: function(t, r) {
          e[t] = r;
        }
      };
    }
  };
}
function ma(e) {
  return e === void 0 && (e = {
    number: {},
    dateTime: {},
    pluralRules: {}
  }), {
    getNumberFormat: De(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.NumberFormat).bind.apply(t, je([void 0], r, !1)))();
    }, {
      cache: ke(e.number),
      strategy: Ue.variadic
    }),
    getDateTimeFormat: De(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.DateTimeFormat).bind.apply(t, je([void 0], r, !1)))();
    }, {
      cache: ke(e.dateTime),
      strategy: Ue.variadic
    }),
    getPluralRules: De(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.PluralRules).bind.apply(t, je([void 0], r, !1)))();
    }, {
      cache: ke(e.pluralRules),
      strategy: Ue.variadic
    })
  };
}
var da = (
  /** @class */
  function() {
    function e(t, r, n, i) {
      r === void 0 && (r = e.defaultLocale);
      var a = this;
      if (this.formatterCache = {
        number: {},
        dateTime: {},
        pluralRules: {}
      }, this.format = function(u) {
        var h = a.formatToParts(u);
        if (h.length === 1)
          return h[0].value;
        var l = h.reduce(function(c, f) {
          return !c.length || f.type !== H.literal || typeof c[c.length - 1] != "string" ? c.push(f.value) : c[c.length - 1] += f.value, c;
        }, []);
        return l.length <= 1 ? l[0] || "" : l;
      }, this.formatToParts = function(u) {
        return he(a.ast, a.locales, a.formatters, a.formats, u, void 0, a.message);
      }, this.resolvedOptions = function() {
        var u;
        return {
          locale: ((u = a.resolvedLocale) === null || u === void 0 ? void 0 : u.toString()) || Intl.NumberFormat.supportedLocalesOf(a.locales)[0]
        };
      }, this.getAst = function() {
        return a.ast;
      }, this.locales = r, this.resolvedLocale = e.resolveLocale(r), typeof t == "string") {
        if (this.message = t, !e.__parse)
          throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
        var o = i || {};
        o.formatters;
        var s = Pi(o, ["formatters"]);
        this.ast = e.__parse(t, y(y({}, s), {
          locale: this.resolvedLocale
        }));
      } else
        this.ast = t;
      if (!Array.isArray(this.ast))
        throw new TypeError("A message must be provided as a String or AST.");
      this.formats = fa(e.formats, n), this.formatters = i && i.formatters || ma(this.formatterCache);
    }
    return Object.defineProperty(e, "defaultLocale", {
      get: function() {
        return e.memoizedDefaultLocale || (e.memoizedDefaultLocale = new Intl.NumberFormat().resolvedOptions().locale), e.memoizedDefaultLocale;
      },
      enumerable: !1,
      configurable: !0
    }), e.memoizedDefaultLocale = null, e.resolveLocale = function(t) {
      if (!(typeof Intl.Locale > "u")) {
        var r = Intl.NumberFormat.supportedLocalesOf(t);
        return r.length > 0 ? new Intl.Locale(r[0]) : new Intl.Locale(typeof t == "string" ? t : t[0]);
      }
    }, e.__parse = oa, e.formats = {
      number: {
        integer: {
          maximumFractionDigits: 0
        },
        currency: {
          style: "currency"
        },
        percent: {
          style: "percent"
        }
      },
      date: {
        short: {
          month: "numeric",
          day: "numeric",
          year: "2-digit"
        },
        medium: {
          month: "short",
          day: "numeric",
          year: "numeric"
        },
        long: {
          month: "long",
          day: "numeric",
          year: "numeric"
        },
        full: {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric"
        }
      },
      time: {
        short: {
          hour: "numeric",
          minute: "numeric"
        },
        medium: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric"
        },
        long: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        },
        full: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        }
      }
    }, e;
  }()
);
function pa(e, t) {
  if (t == null) return;
  if (t in e)
    return e[t];
  const r = t.split(".");
  let n = e;
  for (let i = 0; i < r.length; i++)
    if (typeof n == "object") {
      if (i > 0) {
        const a = r.slice(i, r.length).join(".");
        if (a in n) {
          n = n[a];
          break;
        }
      }
      n = n[r[i]];
    } else
      n = void 0;
  return n;
}
const R = {}, _a = (e, t, r) => r && (t in R || (R[t] = {}), e in R[t] || (R[t][e] = r), r), Hr = (e, t) => {
  if (t == null) return;
  if (t in R && e in R[t])
    return R[t][e];
  const r = Pe(t);
  for (let n = 0; n < r.length; n++) {
    const i = r[n], a = ba(i, e);
    if (a)
      return _a(e, t, a);
  }
};
let mt;
const re = L({});
function ya(e) {
  return mt[e] || null;
}
function Or(e) {
  return e in mt;
}
function ba(e, t) {
  if (!Or(e))
    return null;
  const r = ya(e);
  return pa(r, t);
}
function ga(e) {
  if (e == null) return;
  const t = Pe(e);
  for (let r = 0; r < t.length; r++) {
    const n = t[r];
    if (Or(n))
      return n;
  }
}
function va(e, ...t) {
  delete R[e], re.update((r) => (r[e] = Ei.all([r[e] || {}, ...t]), r));
}
W([re], ([e]) => Object.keys(e));
re.subscribe((e) => mt = e);
const ce = {};
function xa(e, t) {
  ce[e].delete(t), ce[e].size === 0 && delete ce[e];
}
function Ar(e) {
  return ce[e];
}
function Ea(e) {
  return Pe(e).map((t) => {
    const r = Ar(t);
    return [t, r ? [...r] : []];
  }).filter(([, t]) => t.length > 0);
}
function lt(e) {
  return e == null ? !1 : Pe(e).some((t) => {
    var r;
    return (r = Ar(t)) == null ? void 0 : r.size;
  });
}
function Pa(e, t) {
  return Promise.all(t.map((n) => (xa(e, n), n().then((i) => i.default || i)))).then((n) => va(e, ...n));
}
const q = {};
function Cr(e) {
  if (!lt(e))
    return e in q ? q[e] : Promise.resolve();
  const t = Ea(e);
  return q[e] = Promise.all(t.map(([r, n]) => Pa(r, n))).then(() => {
    if (lt(e))
      return Cr(e);
    delete q[e];
  }), q[e];
}
const Sa = {
  number: {
    scientific: {
      notation: "scientific"
    },
    engineering: {
      notation: "engineering"
    },
    compactLong: {
      notation: "compact",
      compactDisplay: "long"
    },
    compactShort: {
      notation: "compact",
      compactDisplay: "short"
    }
  },
  date: {
    short: {
      month: "numeric",
      day: "numeric",
      year: "2-digit"
    },
    medium: {
      month: "short",
      day: "numeric",
      year: "numeric"
    },
    long: {
      month: "long",
      day: "numeric",
      year: "numeric"
    },
    full: {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric"
    }
  },
  time: {
    short: {
      hour: "numeric",
      minute: "numeric"
    },
    medium: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric"
    },
    long: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    },
    full: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    }
  }
}, wa = {
  fallbackLocale: null,
  loadingDelay: 200,
  formats: Sa,
  warnOnMissingMessages: !0,
  handleMissingMessage: void 0,
  ignoreTag: !0
}, Ta = wa;
function X() {
  return Ta;
}
const Ge = L(!1);
var Ha = Object.defineProperty, Oa = Object.defineProperties, Aa = Object.getOwnPropertyDescriptors, Gt = Object.getOwnPropertySymbols, Ca = Object.prototype.hasOwnProperty, Ia = Object.prototype.propertyIsEnumerable, zt = (e, t, r) => t in e ? Ha(e, t, {
  enumerable: !0,
  configurable: !0,
  writable: !0,
  value: r
}) : e[t] = r, Ba = (e, t) => {
  for (var r in t || (t = {})) Ca.call(t, r) && zt(e, r, t[r]);
  if (Gt) for (var r of Gt(t))
    Ia.call(t, r) && zt(e, r, t[r]);
  return e;
}, Na = (e, t) => Oa(e, Aa(t));
let ut;
const pe = L(null);
function $t(e) {
  return e.split("-").map((t, r, n) => n.slice(0, r + 1).join("-")).reverse();
}
function Pe(e, t = X().fallbackLocale) {
  const r = $t(e);
  return t ? [.../* @__PURE__ */ new Set([...r, ...$t(t)])] : r;
}
function U() {
  return ut ?? void 0;
}
pe.subscribe((e) => {
  ut = e ?? void 0, typeof window < "u" && e != null && document.documentElement.setAttribute("lang", e);
});
const Ra = (e) => {
  if (e && ga(e) && lt(e)) {
    const {
      loadingDelay: t
    } = X();
    let r;
    return typeof window < "u" && U() != null && t ? r = window.setTimeout(() => Ge.set(!0), t) : Ge.set(!0), Cr(e).then(() => {
      pe.set(e);
    }).finally(() => {
      clearTimeout(r), Ge.set(!1);
    });
  }
  return pe.set(e);
}, ne = Na(Ba({}, pe), {
  set: Ra
}), Ma = () => typeof window > "u" ? null : window.navigator.language || window.navigator.languages[0], Se = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return (n) => {
    const i = JSON.stringify(n);
    return i in t ? t[i] : t[i] = e(n);
  };
};
var La = Object.defineProperty, _e = Object.getOwnPropertySymbols, Ir = Object.prototype.hasOwnProperty, Br = Object.prototype.propertyIsEnumerable, Vt = (e, t, r) => t in e ? La(e, t, {
  enumerable: !0,
  configurable: !0,
  writable: !0,
  value: r
}) : e[t] = r, dt = (e, t) => {
  for (var r in t || (t = {})) Ir.call(t, r) && Vt(e, r, t[r]);
  if (_e) for (var r of _e(t))
    Br.call(t, r) && Vt(e, r, t[r]);
  return e;
}, Z = (e, t) => {
  var r = {};
  for (var n in e) Ir.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && _e) for (var n of _e(e))
    t.indexOf(n) < 0 && Br.call(e, n) && (r[n] = e[n]);
  return r;
};
const ee = (e, t) => {
  const {
    formats: r
  } = X();
  if (e in r && t in r[e])
    return r[e][t];
  throw new Error(`[svelte-i18n] Unknown "${t}" ${e} format.`);
}, ja = Se((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = Z(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format numbers');
  return n && (i = ee("number", n)), new Intl.NumberFormat(r, i);
}), Da = Se((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = Z(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format dates');
  return n ? i = ee("date", n) : Object.keys(i).length === 0 && (i = ee("date", "short")), new Intl.DateTimeFormat(r, i);
}), Ua = Se((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = Z(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format time values');
  return n ? i = ee("time", n) : Object.keys(i).length === 0 && (i = ee("time", "short")), new Intl.DateTimeFormat(r, i);
}), Fa = (e = {}) => {
  var t = e, {
    locale: r = U()
  } = t, n = Z(t, ["locale"]);
  return ja(dt({
    locale: r
  }, n));
}, ka = (e = {}) => {
  var t = e, {
    locale: r = U()
  } = t, n = Z(t, ["locale"]);
  return Da(dt({
    locale: r
  }, n));
}, Ga = (e = {}) => {
  var t = e, {
    locale: r = U()
  } = t, n = Z(t, ["locale"]);
  return Ua(dt({
    locale: r
  }, n));
}, za = Se(
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  (e, t = U()) => new da(e, t, X().formats, {
    ignoreTag: X().ignoreTag
  })
), $a = (e, t = {}) => {
  var r, n, i, a;
  let o = t;
  typeof e == "object" && (o = e, e = o.id);
  const {
    values: s,
    locale: u = U(),
    default: h
  } = o;
  if (u == null)
    throw new Error("[svelte-i18n] Cannot format a message without first setting the initial locale.");
  let l = Hr(e, u);
  if (!l)
    l = (a = (i = (n = (r = X()).handleMissingMessage) == null ? void 0 : n.call(r, {
      locale: u,
      id: e,
      defaultValue: h
    })) != null ? i : h) != null ? a : e;
  else if (typeof l != "string")
    return console.warn(`[svelte-i18n] Message with id "${e}" must be of type "string", found: "${typeof l}". Gettin its value through the "$format" method is deprecated; use the "json" method instead.`), l;
  if (!s)
    return l;
  let c = l;
  try {
    c = za(l, u).format(s);
  } catch (f) {
    f instanceof Error && console.warn(`[svelte-i18n] Message "${e}" has syntax error:`, f.message);
  }
  return c;
}, Va = (e, t) => Ga(t).format(e), Xa = (e, t) => ka(t).format(e), Wa = (e, t) => Fa(t).format(e), Za = (e, t = U()) => Hr(e, t);
W([ne, re], () => $a);
W([ne], () => Va);
W([ne], () => Xa);
W([ne], () => Wa);
W([ne, re], () => Za);
var we = {}, Nr = {
  exports: {}
};
(function(e) {
  function t(r) {
    return r && r.__esModule ? r : {
      default: r
    };
  }
  e.exports = t, e.exports.__esModule = !0, e.exports.default = e.exports;
})(Nr);
var Te = Nr.exports, He = {};
Object.defineProperty(He, "__esModule", {
  value: !0
});
He.default = void 0;
var Ya = {
  // Options
  items_per_page: "/ page",
  jump_to: "Go to",
  jump_to_confirm: "confirm",
  page: "Page",
  // Pagination
  prev_page: "Previous Page",
  next_page: "Next Page",
  prev_5: "Previous 5 Pages",
  next_5: "Next 5 Pages",
  prev_3: "Previous 3 Pages",
  next_3: "Next 3 Pages",
  page_size: "Page Size"
};
He.default = Ya;
var Oe = {}, ie = {}, Ae = {}, Rr = {
  exports: {}
}, Mr = {
  exports: {}
}, Lr = {
  exports: {}
}, jr = {
  exports: {}
};
(function(e) {
  function t(r) {
    "@babel/helpers - typeof";
    return e.exports = t = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(n) {
      return typeof n;
    } : function(n) {
      return n && typeof Symbol == "function" && n.constructor === Symbol && n !== Symbol.prototype ? "symbol" : typeof n;
    }, e.exports.__esModule = !0, e.exports.default = e.exports, t(r);
  }
  e.exports = t, e.exports.__esModule = !0, e.exports.default = e.exports;
})(jr);
var Dr = jr.exports, Ur = {
  exports: {}
};
(function(e) {
  var t = Dr.default;
  function r(n, i) {
    if (t(n) != "object" || !n) return n;
    var a = n[Symbol.toPrimitive];
    if (a !== void 0) {
      var o = a.call(n, i || "default");
      if (t(o) != "object") return o;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return (i === "string" ? String : Number)(n);
  }
  e.exports = r, e.exports.__esModule = !0, e.exports.default = e.exports;
})(Ur);
var qa = Ur.exports;
(function(e) {
  var t = Dr.default, r = qa;
  function n(i) {
    var a = r(i, "string");
    return t(a) == "symbol" ? a : a + "";
  }
  e.exports = n, e.exports.__esModule = !0, e.exports.default = e.exports;
})(Lr);
var Ka = Lr.exports;
(function(e) {
  var t = Ka;
  function r(n, i, a) {
    return (i = t(i)) in n ? Object.defineProperty(n, i, {
      value: a,
      enumerable: !0,
      configurable: !0,
      writable: !0
    }) : n[i] = a, n;
  }
  e.exports = r, e.exports.__esModule = !0, e.exports.default = e.exports;
})(Mr);
var Qa = Mr.exports;
(function(e) {
  var t = Qa;
  function r(i, a) {
    var o = Object.keys(i);
    if (Object.getOwnPropertySymbols) {
      var s = Object.getOwnPropertySymbols(i);
      a && (s = s.filter(function(u) {
        return Object.getOwnPropertyDescriptor(i, u).enumerable;
      })), o.push.apply(o, s);
    }
    return o;
  }
  function n(i) {
    for (var a = 1; a < arguments.length; a++) {
      var o = arguments[a] != null ? arguments[a] : {};
      a % 2 ? r(Object(o), !0).forEach(function(s) {
        t(i, s, o[s]);
      }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(i, Object.getOwnPropertyDescriptors(o)) : r(Object(o)).forEach(function(s) {
        Object.defineProperty(i, s, Object.getOwnPropertyDescriptor(o, s));
      });
    }
    return i;
  }
  e.exports = n, e.exports.__esModule = !0, e.exports.default = e.exports;
})(Rr);
var Ja = Rr.exports, Ce = {};
Object.defineProperty(Ce, "__esModule", {
  value: !0
});
Ce.commonLocale = void 0;
Ce.commonLocale = {
  yearFormat: "YYYY",
  dayFormat: "D",
  cellMeridiemFormat: "A",
  monthBeforeYear: !0
};
var eo = Te.default;
Object.defineProperty(Ae, "__esModule", {
  value: !0
});
Ae.default = void 0;
var Xt = eo(Ja), to = Ce, ro = (0, Xt.default)((0, Xt.default)({}, to.commonLocale), {}, {
  locale: "en_US",
  today: "Today",
  now: "Now",
  backToToday: "Back to today",
  ok: "OK",
  clear: "Clear",
  week: "Week",
  month: "Month",
  year: "Year",
  timeSelect: "select time",
  dateSelect: "select date",
  weekSelect: "Choose a week",
  monthSelect: "Choose a month",
  yearSelect: "Choose a year",
  decadeSelect: "Choose a decade",
  dateFormat: "M/D/YYYY",
  dateTimeFormat: "M/D/YYYY HH:mm:ss",
  previousMonth: "Previous month (PageUp)",
  nextMonth: "Next month (PageDown)",
  previousYear: "Last year (Control + left)",
  nextYear: "Next year (Control + right)",
  previousDecade: "Last decade",
  nextDecade: "Next decade",
  previousCentury: "Last century",
  nextCentury: "Next century"
});
Ae.default = ro;
var ae = {};
Object.defineProperty(ae, "__esModule", {
  value: !0
});
ae.default = void 0;
const no = {
  placeholder: "Select time",
  rangePlaceholder: ["Start time", "End time"]
};
ae.default = no;
var Fr = Te.default;
Object.defineProperty(ie, "__esModule", {
  value: !0
});
ie.default = void 0;
var io = Fr(Ae), ao = Fr(ae);
const oo = {
  lang: Object.assign({
    placeholder: "Select date",
    yearPlaceholder: "Select year",
    quarterPlaceholder: "Select quarter",
    monthPlaceholder: "Select month",
    weekPlaceholder: "Select week",
    rangePlaceholder: ["Start date", "End date"],
    rangeYearPlaceholder: ["Start year", "End year"],
    rangeQuarterPlaceholder: ["Start quarter", "End quarter"],
    rangeMonthPlaceholder: ["Start month", "End month"],
    rangeWeekPlaceholder: ["Start week", "End week"]
  }, io.default),
  timePickerLocale: Object.assign({}, ao.default)
};
ie.default = oo;
var so = Te.default;
Object.defineProperty(Oe, "__esModule", {
  value: !0
});
Oe.default = void 0;
var lo = so(ie);
Oe.default = lo.default;
var Ie = Te.default;
Object.defineProperty(we, "__esModule", {
  value: !0
});
we.default = void 0;
var uo = Ie(He), ho = Ie(Oe), co = Ie(ie), fo = Ie(ae);
const A = "${label} is not a valid ${type}", mo = {
  locale: "en",
  Pagination: uo.default,
  DatePicker: co.default,
  TimePicker: fo.default,
  Calendar: ho.default,
  global: {
    placeholder: "Please select",
    close: "Close"
  },
  Table: {
    filterTitle: "Filter menu",
    filterConfirm: "OK",
    filterReset: "Reset",
    filterEmptyText: "No filters",
    filterCheckAll: "Select all items",
    filterSearchPlaceholder: "Search in filters",
    emptyText: "No data",
    selectAll: "Select current page",
    selectInvert: "Invert current page",
    selectNone: "Clear all data",
    selectionAll: "Select all data",
    sortTitle: "Sort",
    expand: "Expand row",
    collapse: "Collapse row",
    triggerDesc: "Click to sort descending",
    triggerAsc: "Click to sort ascending",
    cancelSort: "Click to cancel sorting"
  },
  Tour: {
    Next: "Next",
    Previous: "Previous",
    Finish: "Finish"
  },
  Modal: {
    okText: "OK",
    cancelText: "Cancel",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Cancel"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Search here",
    itemUnit: "item",
    itemsUnit: "items",
    remove: "Remove",
    selectCurrent: "Select current page",
    removeCurrent: "Remove current page",
    selectAll: "Select all data",
    deselectAll: "Deselect all data",
    removeAll: "Remove all data",
    selectInvert: "Invert current page"
  },
  Upload: {
    uploading: "Uploading...",
    removeFile: "Remove file",
    uploadError: "Upload error",
    previewFile: "Preview file",
    downloadFile: "Download file"
  },
  Empty: {
    description: "No data"
  },
  Icon: {
    icon: "icon"
  },
  Text: {
    edit: "Edit",
    copy: "Copy",
    copied: "Copied",
    expand: "Expand",
    collapse: "Collapse"
  },
  Form: {
    optional: "(optional)",
    defaultValidateMessages: {
      default: "Field validation error for ${label}",
      required: "Please enter ${label}",
      enum: "${label} must be one of [${enum}]",
      whitespace: "${label} cannot be a blank character",
      date: {
        format: "${label} date format is invalid",
        parse: "${label} cannot be converted to a date",
        invalid: "${label} is an invalid date"
      },
      types: {
        string: A,
        method: A,
        array: A,
        object: A,
        number: A,
        date: A,
        boolean: A,
        integer: A,
        float: A,
        regexp: A,
        email: A,
        url: A,
        hex: A
      },
      string: {
        len: "${label} must be ${len} characters",
        min: "${label} must be at least ${min} characters",
        max: "${label} must be up to ${max} characters",
        range: "${label} must be between ${min}-${max} characters"
      },
      number: {
        len: "${label} must be equal to ${len}",
        min: "${label} must be minimum ${min}",
        max: "${label} must be maximum ${max}",
        range: "${label} must be between ${min}-${max}"
      },
      array: {
        len: "Must be ${len} ${label}",
        min: "At least ${min} ${label}",
        max: "At most ${max} ${label}",
        range: "The amount of ${label} must be between ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} does not match the pattern ${pattern}"
      }
    }
  },
  Image: {
    preview: "Preview"
  },
  QRCode: {
    expired: "QR code expired",
    refresh: "Refresh",
    scanned: "Scanned"
  },
  ColorPicker: {
    presetEmpty: "Empty",
    transparent: "Transparent",
    singleColor: "Single",
    gradientColor: "Gradient"
  }
};
we.default = mo;
var kr = we;
const Gr = /* @__PURE__ */ ht(kr), po = /* @__PURE__ */ Kt({
  __proto__: null,
  default: Gr
}, [kr]);
var zr = {
  exports: {}
};
(function(e, t) {
  (function(r, n) {
    e.exports = n();
  })(Qr, function() {
    return {
      name: "en",
      weekdays: "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),
      months: "January_February_March_April_May_June_July_August_September_October_November_December".split("_"),
      ordinal: function(r) {
        var n = ["th", "st", "nd", "rd"], i = r % 100;
        return "[" + r + (n[(i - 20) % 10] || n[i] || n[0]) + "]";
      }
    };
  });
})(zr);
var $r = zr.exports;
const _o = /* @__PURE__ */ ht($r), yo = /* @__PURE__ */ Kt({
  __proto__: null,
  default: _o
}, [$r]), bo = () => (qt.locale("en"), Gr), go = {
  ar: "ar_EG",
  az: "az_AZ",
  bg: "bg_BG",
  bn: "bn_BD",
  be: "by_BY",
  // Belarusian (Belarus)
  ca: "ca_ES",
  cs: "cs_CZ",
  da: "da_DK",
  de: "de_DE",
  el: "el_GR",
  en_gb: "en_GB",
  en: "en_US",
  es: "es_ES",
  et: "et_EE",
  eu: "eu_ES",
  // Basque
  fa: "fa_IR",
  fi: "fi_FI",
  fr_be: "fr_BE",
  fr_ca: "fr_CA",
  fr_fr: "fr_FR",
  fr: "fr_FR",
  ga: "ga_IE",
  // Irish
  gl: "gl_ES",
  // Galician
  he: "he_IL",
  hi: "hi_IN",
  hr: "hr_HR",
  hu: "hu_HU",
  am: "hy_AM",
  // Armenian
  id: "id_ID",
  is: "is_IS",
  it: "it_IT",
  ja: "ja_JP",
  ka: "ka_GE",
  // Georgian
  kk: "kk_KZ",
  // Kazakh
  km: "km_KH",
  // Khmer
  kmr: "kmr_IQ",
  // Kurdish (Northern)
  kn: "kn_IN",
  // Kannada
  ko: "ko_KR",
  ku: "ku_IQ",
  // Kurdish (Central)
  lt: "lt_LT",
  lv: "lv_LV",
  mk: "mk_MK",
  // Macedonian
  ml: "ml_IN",
  // Malayalam
  mn: "mn_MN",
  // Mongolian
  ms: "ms_MY",
  my: "my_MM",
  // Burmese
  nb: "nb_NO",
  // Norwegian Bokmål
  ne: "ne_NP",
  // Nepali
  nl_be: "nl_BE",
  // Dutch (Belgium)
  nl_nl: "nl_NL",
  // Dutch (Netherlands)
  nl: "nl_NL",
  // Dutch (Netherlands)
  pl: "pl_PL",
  pt_br: "pt_BR",
  // Portuguese (Brazil)
  pt_pt: "pt_PT",
  // Portuguese (Portugal)
  pt: "pt_PT",
  ro: "ro_RO",
  ru: "ru_RU",
  si: "si_LK",
  // Sinhala
  sk: "sk_SK",
  sl: "sl_SI",
  sr: "sr_RS",
  // Serbian
  sv: "sv_SE",
  ta: "ta_IN",
  // Tamil
  th: "th_TH",
  tk: "tk_TK",
  // Turkmen
  tr: "tr_TR",
  uk: "uk_UA",
  // Ukrainian
  ur: "ur_PK",
  // Urdu
  uz: "uz_UZ",
  // Uzbek
  vi: "vi_VN",
  zh: "zh_CN",
  // Chinese (Simplified),
  zh_cn: "zh_CN",
  // Chinese (Simplified)
  zh_hk: "zh_HK",
  // Chinese (Hong Kong)
  zh_tw: "zh_TW"
  // Chinese (Taiwan)
}, ze = {
  ar_EG: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ar_EG-DjbfCkXc.js").then((t) => t.a), import("./ar-_Bxr7LKy.js").then((t) => t.a)]);
    return {
      antd: e,
      dayjs: "ar"
    };
  },
  az_AZ: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./az_AZ-DjLGeoBk.js").then((t) => t.a), import("./az-C9aMhQGm.js").then((t) => t.a)]);
    return {
      antd: e,
      dayjs: "az"
    };
  },
  bg_BG: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./bg_BG-BNnT9_gl.js").then((t) => t.b), import("./bg-D9L9Q_Qs.js").then((t) => t.b)]);
    return {
      antd: e,
      dayjs: "bg"
    };
  },
  bn_BD: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./bn_BD-K-pXlEI1.js").then((t) => t.b), import("./bn-CZSRRVu3.js").then((t) => t.b)]);
    return {
      antd: e,
      dayjs: "bn"
    };
  },
  by_BY: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./by_BY-M421BpFt.js").then((t) => t.b),
      import("./be-B_0M8FB2.js").then((t) => t.b)
      // Belarusian (Belarus)
    ]);
    return {
      antd: e,
      dayjs: "be"
    };
  },
  ca_ES: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ca_ES-CtMRi_lp.js").then((t) => t.c), import("./ca-LF1vtsNh.js").then((t) => t.c)]);
    return {
      antd: e,
      dayjs: "ca"
    };
  },
  cs_CZ: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./cs_CZ-CMGB-bh2.js").then((t) => t.c), import("./cs-DfVfVJHt.js").then((t) => t.c)]);
    return {
      antd: e,
      dayjs: "cs"
    };
  },
  da_DK: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./da_DK-BVwpiPhr.js").then((t) => t.d), import("./da-B8N92aQ2.js").then((t) => t.d)]);
    return {
      antd: e,
      dayjs: "da"
    };
  },
  de_DE: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./de_DE-DKRUrKhi.js").then((t) => t.d), import("./de-DG5t2i7V.js").then((t) => t.d)]);
    return {
      antd: e,
      dayjs: "de"
    };
  },
  el_GR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./el_GR-zseOuDgt.js").then((t) => t.e), import("./el-B7estN5H.js").then((t) => t.e)]);
    return {
      antd: e,
      dayjs: "el"
    };
  },
  en_GB: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./en_GB-By_qJYVG.js").then((t) => t.e), import("./en-gb-C5vsIN3f.js").then((t) => t.e)]);
    return {
      antd: e,
      dayjs: "en-gb"
    };
  },
  en_US: async () => {
    const [{
      default: e
    }] = await Promise.all([Promise.resolve().then(() => po), Promise.resolve().then(() => yo)]);
    return {
      antd: e,
      dayjs: "en"
    };
  },
  es_ES: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./es_ES-Cmg0XZsS.js").then((t) => t.e), import("./es-D8juKEih.js").then((t) => t.e)]);
    return {
      antd: e,
      dayjs: "es"
    };
  },
  et_EE: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./et_EE-BsXy1C1G.js").then((t) => t.e), import("./et-B9nBLCVe.js").then((t) => t.e)]);
    return {
      antd: e,
      dayjs: "et"
    };
  },
  eu_ES: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./eu_ES-CjK5jWVX.js").then((t) => t.e),
      import("./eu-BObVNlFc.js").then((t) => t.e)
      // Basque
    ]);
    return {
      antd: e,
      dayjs: "eu"
    };
  },
  fa_IR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./fa_IR-C3ZY8BRf.js").then((t) => t.f), import("./fa-CuCwxgkg.js").then((t) => t.f)]);
    return {
      antd: e,
      dayjs: "fa"
    };
  },
  fi_FI: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./fi_FI-CpOGzuAO.js").then((t) => t.f), import("./fi-CVn9RdRw.js").then((t) => t.f)]);
    return {
      antd: e,
      dayjs: "fi"
    };
  },
  fr_BE: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./fr_BE-BGilZ-Mg.js").then((t) => t.f), import("./fr-puCbW1lX.js").then((t) => t.f)]);
    return {
      antd: e,
      dayjs: "fr"
    };
  },
  fr_CA: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./fr_CA-BzuMBlaB.js").then((t) => t.f), import("./fr-ca-Bfu0WLJg.js").then((t) => t.f)]);
    return {
      antd: e,
      dayjs: "fr-ca"
    };
  },
  fr_FR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./fr_FR-DwXFJN6w.js").then((t) => t.f), import("./fr-puCbW1lX.js").then((t) => t.f)]);
    return {
      antd: e,
      dayjs: "fr"
    };
  },
  ga_IE: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ga_IE-DC1tA_zH.js").then((t) => t.g),
      import("./ga-CrIX8Gyv.js").then((t) => t.g)
      // Irish
    ]);
    return {
      antd: e,
      dayjs: "ga"
    };
  },
  gl_ES: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./gl_ES-CwalKvTz.js").then((t) => t.g),
      import("./gl-vw17Prq6.js").then((t) => t.g)
      // Galician
    ]);
    return {
      antd: e,
      dayjs: "gl"
    };
  },
  he_IL: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./he_IL-CPc2hvrg.js").then((t) => t.h), import("./he-rGFDqiXs.js").then((t) => t.h)]);
    return {
      antd: e,
      dayjs: "he"
    };
  },
  hi_IN: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./hi_IN-BNvKkYCd.js").then((t) => t.h), import("./hi-lChp-C5g.js").then((t) => t.h)]);
    return {
      antd: e,
      dayjs: "hi"
    };
  },
  hr_HR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./hr_HR-CQ43PN1v.js").then((t) => t.h), import("./hr-B00aagTV.js").then((t) => t.h)]);
    return {
      antd: e,
      dayjs: "hr"
    };
  },
  hu_HU: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./hu_HU-8aI7cEKa.js").then((t) => t.h), import("./hu-Ch_lQKIb.js").then((t) => t.h)]);
    return {
      antd: e,
      dayjs: "hu"
    };
  },
  hy_AM: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./hy_AM-BNzWL745.js").then((t) => t.h),
      import("./am-k01w20M_.js").then((t) => t.a)
      // Armenian
    ]);
    return {
      antd: e,
      dayjs: "am"
    };
  },
  id_ID: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./id_ID-UyIDg-em.js").then((t) => t.i), import("./id-DWPtp06i.js").then((t) => t.i)]);
    return {
      antd: e,
      dayjs: "id"
    };
  },
  is_IS: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./is_IS-eKmA3qSO.js").then((t) => t.i), import("./is-DH9vkF-T.js").then((t) => t.i)]);
    return {
      antd: e,
      dayjs: "is"
    };
  },
  it_IT: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./it_IT-BJjci4fQ.js").then((t) => t.i), import("./it-DJH1O-xC.js").then((t) => t.i)]);
    return {
      antd: e,
      dayjs: "it"
    };
  },
  ja_JP: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ja_JP-DQONyNGz.js").then((t) => t.j), import("./ja-BBRTYS-B.js").then((t) => t.j)]);
    return {
      antd: e,
      dayjs: "ja"
    };
  },
  ka_GE: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ka_GE-Cdcz9tQg.js").then((t) => t.k),
      import("./ka-C6x0XAo-.js").then((t) => t.k)
      // Georgian
    ]);
    return {
      antd: e,
      dayjs: "ka"
    };
  },
  kk_KZ: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./kk_KZ-DqXKz9oR.js").then((t) => t.k),
      import("./kk-PI-_KD8G.js").then((t) => t.k)
      // Kazakh
    ]);
    return {
      antd: e,
      dayjs: "kk"
    };
  },
  km_KH: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./km_KH-BKYYmFh6.js").then((t) => t.k),
      import("./km-B5jniK2Z.js").then((t) => t.k)
      // Khmer
    ]);
    return {
      antd: e,
      dayjs: "km"
    };
  },
  kmr_IQ: async () => {
    const [e] = await Promise.all([
      import("./kmr_IQ-DJSY61No.js").then((t) => t.k)
      // Not available in Day.js, so no need to load a locale file.
    ]);
    return {
      antd: e.default,
      dayjs: ""
    };
  },
  kn_IN: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./kn_IN-DJTuRTl1.js").then((t) => t.k),
      import("./kn-DmgbE1qb.js").then((t) => t.k)
      // Kannada
    ]);
    return {
      antd: e,
      dayjs: "kn"
    };
  },
  ko_KR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ko_KR-COYOZM4w.js").then((t) => t.k), import("./ko-sl2g0fZc.js").then((t) => t.k)]);
    return {
      antd: e,
      dayjs: "ko"
    };
  },
  ku_IQ: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ku_IQ-BtNbqZlr.js").then((t) => t.k),
      import("./ku-BeYT36mZ.js").then((t) => t.k)
      // Kurdish (Central)
    ]);
    return {
      antd: e,
      dayjs: "ku"
    };
  },
  lt_LT: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./lt_LT-CAdYOMS-.js").then((t) => t.l), import("./lt-CFV7WKVn.js").then((t) => t.l)]);
    return {
      antd: e,
      dayjs: "lt"
    };
  },
  lv_LV: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./lv_LV-DJmfJM4N.js").then((t) => t.l), import("./lv-C4hUzSGm.js").then((t) => t.l)]);
    return {
      antd: e,
      dayjs: "lv"
    };
  },
  mk_MK: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./mk_MK-grUFwzhK.js").then((t) => t.m),
      import("./mk-DDJJknaK.js").then((t) => t.m)
      // Macedonian
    ]);
    return {
      antd: e,
      dayjs: "mk"
    };
  },
  ml_IN: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ml_IN-mhNhpsku.js").then((t) => t.m),
      import("./ml-CaAzHuhJ.js").then((t) => t.m)
      // Malayalam
    ]);
    return {
      antd: e,
      dayjs: "ml"
    };
  },
  mn_MN: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./mn_MN-DnwY7noF.js").then((t) => t.m),
      import("./mn-BvHwaSye.js").then((t) => t.m)
      // Mongolian
    ]);
    return {
      antd: e,
      dayjs: "mn"
    };
  },
  ms_MY: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ms_MY-CoPay69p.js").then((t) => t.m), import("./ms-Cn0E5yUQ.js").then((t) => t.m)]);
    return {
      antd: e,
      dayjs: "ms"
    };
  },
  my_MM: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./my_MM-BWFCjdCw.js").then((t) => t.m),
      import("./my-CEHqLi1a.js").then((t) => t.m)
      // Burmese
    ]);
    return {
      antd: e,
      dayjs: "my"
    };
  },
  nb_NO: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./nb_NO-DwRcIdWz.js").then((t) => t.n),
      import("./nb-Djvc-zmZ.js").then((t) => t.n)
      // Norwegian Bokmål
    ]);
    return {
      antd: e,
      dayjs: "nb"
    };
  },
  ne_NP: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ne_NP-mdDI0hFE.js").then((t) => t.n),
      import("./ne-BSv7Vf2j.js").then((t) => t.n)
      // Nepali
    ]);
    return {
      antd: e,
      dayjs: "ne"
    };
  },
  nl_BE: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./nl_BE-HH1AmtAE.js").then((t) => t.n),
      import("./nl-be-CL78_3JX.js").then((t) => t.n)
      // Dutch (Belgium)
    ]);
    return {
      antd: e,
      dayjs: "nl-be"
    };
  },
  nl_NL: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./nl_NL-gBjvW6D-.js").then((t) => t.n),
      import("./nl-rZrxmCzI.js").then((t) => t.n)
      // Dutch (Netherlands)
    ]);
    return {
      antd: e,
      dayjs: "nl"
    };
  },
  pl_PL: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./pl_PL-CcNWdj54.js").then((t) => t.p), import("./pl-DigTmzu_.js").then((t) => t.p)]);
    return {
      antd: e,
      dayjs: "pl"
    };
  },
  pt_BR: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./pt_BR-Dm86Q7fM.js").then((t) => t.p),
      import("./pt-br-5H1Qr2m9.js").then((t) => t.p)
      // Portuguese (Brazil)
    ]);
    return {
      antd: e,
      dayjs: "pt-br"
    };
  },
  pt_PT: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./pt_PT-yY56OZEj.js").then((t) => t.p),
      import("./pt-D_sbE6jn.js").then((t) => t.p)
      // Portuguese (Portugal)
    ]);
    return {
      antd: e,
      dayjs: "pt"
    };
  },
  ro_RO: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ro_RO-CsB1Ndzb.js").then((t) => t.r), import("./ro-TY1aOL2z.js").then((t) => t.r)]);
    return {
      antd: e,
      dayjs: "ro"
    };
  },
  ru_RU: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./ru_RU-C4BJlB6V.js").then((t) => t.r), import("./ru-DF5Ti5Dv.js").then((t) => t.r)]);
    return {
      antd: e,
      dayjs: "ru"
    };
  },
  si_LK: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./si_LK-DBxS0H3f.js").then((t) => t.s),
      import("./si-CD95rm8q.js").then((t) => t.s)
      // Sinhala
    ]);
    return {
      antd: e,
      dayjs: "si"
    };
  },
  sk_SK: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./sk_SK-GTvpXtDm.js").then((t) => t.s), import("./sk-DarLnb4q.js").then((t) => t.s)]);
    return {
      antd: e,
      dayjs: "sk"
    };
  },
  sl_SI: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./sl_SI-Cq8-3RuS.js").then((t) => t.s), import("./sl-Y7uO51h_.js").then((t) => t.s)]);
    return {
      antd: e,
      dayjs: "sl"
    };
  },
  sr_RS: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./sr_RS-BQU3traQ.js").then((t) => t.s),
      import("./sr-Lm_pAyR_.js").then((t) => t.s)
      // Serbian
    ]);
    return {
      antd: e,
      dayjs: "sr"
    };
  },
  sv_SE: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./sv_SE-BOEdhmym.js").then((t) => t.s), import("./sv-DbspGKgW.js").then((t) => t.s)]);
    return {
      antd: e,
      dayjs: "sv"
    };
  },
  ta_IN: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ta_IN-Bz3NEtG1.js").then((t) => t.t),
      import("./ta-hhJeRIDR.js").then((t) => t.t)
      // Tamil
    ]);
    return {
      antd: e,
      dayjs: "ta"
    };
  },
  th_TH: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./th_TH-Bs3JSbu2.js").then((t) => t.t), import("./th-DFB9dUOg.js").then((t) => t.t)]);
    return {
      antd: e,
      dayjs: "th"
    };
  },
  tk_TK: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./tk_TK-9he0-nt7.js").then((t) => t.t),
      import("./tk-CbWnRyhb.js").then((t) => t.t)
      // Turkmen
    ]);
    return {
      antd: e,
      dayjs: "tk"
    };
  },
  tr_TR: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./tr_TR-sd00saAD.js").then((t) => t.t), import("./tr-C6K-1C4e.js").then((t) => t.t)]);
    return {
      antd: e,
      dayjs: "tr"
    };
  },
  uk_UA: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./uk_UA-geC37J92.js").then((t) => t.u),
      import("./uk-CtO2HE6u.js").then((t) => t.u)
      // Ukrainian
    ]);
    return {
      antd: e,
      dayjs: "uk"
    };
  },
  ur_PK: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./ur_PK-CENqMVrB.js").then((t) => t.u),
      import("./ur-Dm0imveC.js").then((t) => t.u)
      // Urdu
    ]);
    return {
      antd: e,
      dayjs: "ur"
    };
  },
  uz_UZ: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./uz_UZ-Xxt6CS-w.js").then((t) => t.u),
      import("./uz-BjJrfFFV.js").then((t) => t.u)
      // Uzbek
    ]);
    return {
      antd: e,
      dayjs: "uz"
    };
  },
  vi_VN: async () => {
    const [{
      default: e
    }] = await Promise.all([import("./vi_VN-Cbbj5Qvi.js").then((t) => t.v), import("./vi-j8yRxxTV.js").then((t) => t.v)]);
    return {
      antd: e,
      dayjs: "vi"
    };
  },
  zh_CN: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./zh_CN-_5TA0Q4L.js").then((t) => t.z),
      import("./zh-cn-iNZvmFRg.js").then((t) => t.z)
      // Chinese (Simplified)
    ]);
    return {
      antd: e,
      dayjs: "zh-cn"
    };
  },
  zh_HK: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./zh_HK-C5T-Ahkh.js").then((t) => t.z),
      import("./zh-hk-BpA38KE-.js").then((t) => t.z)
      // Chinese (Hong Kong)
    ]);
    return {
      antd: e,
      dayjs: "zh-hk"
    };
  },
  zh_TW: async () => {
    const [{
      default: e
    }] = await Promise.all([
      import("./zh_TW-Bv71sVoL.js").then((t) => t.z),
      import("./zh-tw-CHk613_a.js").then((t) => t.z)
      // Chinese (Taiwan)
    ]);
    return {
      antd: e,
      dayjs: "zh-tw"
    };
  }
};
function vo(e) {
  if (!e)
    return "en_US";
  let t = "en_US";
  const r = e.replace("-", "_").split("_");
  return r.length === 1 ? t = go[r[0].toLowerCase()] || "en_US" : r.length === 2 && (t = `${r[0].toLowerCase()}_${r[1].toUpperCase()}`), t;
}
const xo = (e, t) => si(e, (r) => {
  Object.keys(t).forEach((n) => {
    const i = n.split(".");
    let a = r;
    for (let o = 0; o < i.length - 1; o++) {
      const s = i[o];
      a[s] || (a[s] = {}), a = a[s];
    }
    a[i[i.length - 1]] = /* @__PURE__ */ I.jsx(Ze, {
      slot: t[n],
      clone: !0
    });
  });
}), Wt = kn(({
  slots: e,
  themeMode: t,
  id: r,
  className: n,
  style: i,
  locale: a = vo(Ma()),
  getTargetContainer: o,
  getPopupContainer: s,
  renderEmpty: u,
  setSlotParams: h,
  children: l,
  component: c,
  ...f
}) => {
  var _;
  const [m, E] = Zt(() => bo()), P = {
    dark: t === "dark",
    ...((_ = f.theme) == null ? void 0 : _.algorithm) || {}
  }, b = Re(s), x = Re(o), w = Re(u);
  Yt(() => {
    (a && ze[a] ? ze[a] : ze.en_US)().then(({
      antd: g,
      dayjs: O
    }) => {
      E(g), qt.locale(O);
    });
  }, [a]);
  const T = c || rn;
  return /* @__PURE__ */ I.jsx("div", {
    id: r,
    className: n,
    style: i,
    children: /* @__PURE__ */ I.jsx(tn, {
      hashPriority: "high",
      container: document.body,
      children: /* @__PURE__ */ I.jsx(T, {
        prefixCls: "ms-gr-ant",
        ...xo(f, e),
        locale: m,
        getPopupContainer: b,
        getTargetContainer: x,
        renderEmpty: e.renderEmpty ? qn({
          slots: e,
          key: "renderEmpty"
        }) : w,
        theme: {
          cssVar: !0,
          ...f.theme,
          algorithm: Object.keys(P).map((S) => {
            switch (S) {
              case "dark":
                return P[S] ? _t.darkAlgorithm : null;
              case "compact":
                return P[S] ? _t.compactAlgorithm : null;
              default:
                return null;
            }
          }).filter(Boolean)
        },
        children: l
      })
    })
  });
}), So = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  ConfigProvider: Wt,
  default: Wt
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  Oe as a,
  ie as b,
  Ce as c,
  ae as d,
  He as e,
  So as f,
  Te as i,
  Ja as o
};
