import { m as ee, i as te } from "./Index-BH7uWXrq.js";
const B = window.ms_globals.antd.ConfigProvider, v = window.ms_globals.React;
function C() {
}
function ne(e) {
  return e();
}
function se(e) {
  return typeof e == "function";
}
function D(e, ...t) {
  if (e == null) {
    for (const n of t) n(void 0);
    return C;
  }
  const o = e.subscribe(...t);
  return o.unsubscribe ? () => o.unsubscribe() : o;
}
function G(e) {
  let t;
  return D(e, (o) => t = o)(), t;
}
const x = [];
function oe(e, t) {
  return {
    subscribe: b(e, t).subscribe
  };
}
function b(e, t = C) {
  let o;
  const n = /* @__PURE__ */ new Set();
  function r(i) {
    if (u = i, ((l = e) != l ? u == u : l !== u || l && typeof l == "object" || typeof l == "function") && (e = i, o)) {
      const p = !x.length;
      for (const f of n) f[1](), x.push(f, e);
      if (p) {
        for (let f = 0; f < x.length; f += 2) x[f][0](x[f + 1]);
        x.length = 0;
      }
    }
    var l, u;
  }
  function s(i) {
    r(i(e));
  }
  return {
    set: r,
    update: s,
    subscribe: function(i, l = C) {
      const u = [i, l];
      return n.add(u), n.size === 1 && (o = t(r, s) || C), i(e), () => {
        n.delete(u), n.size === 0 && o && (o(), o = null);
      };
    }
  };
}
function We(e, t, o) {
  const n = !Array.isArray(e), r = n ? [e] : e;
  if (!r.every(Boolean)) throw new Error("derived() expects stores as input, got a falsy value");
  const s = t.length < 2;
  return oe(o, (i, l) => {
    let u = !1;
    const p = [];
    let f = 0, m = C;
    const a = () => {
      if (f) return;
      m();
      const g = t(n ? p[0] : p, i, l);
      s ? i(g) : m = se(g) ? g : C;
    }, _ = r.map((g, h) => D(g, (y) => {
      p[h] = y, f &= ~(1 << h), u && a();
    }, () => {
      f |= 1 << h;
    }));
    return u = !0, a(), function() {
      _.forEach(ne), m(), u = !1;
    };
  });
}
const {
  getContext: re,
  setContext: ie
} = window.__gradio__svelte__internal, le = "$$ms-gr-config-type-key";
function ce(e) {
  ie(le, e);
}
const ae = "$$ms-gr-loading-status-key";
function ue() {
  const e = window.ms_globals.loadingKey++, t = re(ae);
  return (o) => {
    if (!t || !o)
      return;
    const {
      loadingStatusMap: n,
      options: r
    } = t, {
      generating: s,
      error: i
    } = G(r);
    (o == null ? void 0 : o.status) === "pending" || i && (o == null ? void 0 : o.status) === "error" || (s && (o == null ? void 0 : o.status)) === "generating" ? n.update(({
      map: l
    }) => (l.set(e, o), {
      map: l
    })) : n.update(({
      map: l
    }) => (l.delete(e), {
      map: l
    }));
  };
}
const {
  getContext: I,
  setContext: S
} = window.__gradio__svelte__internal, fe = "$$ms-gr-slots-key";
function me() {
  const e = b({});
  return S(fe, e);
}
const V = "$$ms-gr-slot-params-mapping-fn-key";
function _e() {
  return I(V);
}
function de(e) {
  return S(V, b(e));
}
const pe = "$$ms-gr-slot-params-key";
function ge() {
  const e = S(pe, b({}));
  return (t, o) => {
    e.update((n) => typeof o == "function" ? {
      ...n,
      [t]: o(n[t])
    } : {
      ...n,
      [t]: o
    });
  };
}
const Y = "$$ms-gr-sub-index-context-key";
function be() {
  return I(Y) || null;
}
function N(e) {
  return S(Y, e);
}
function he(e, t, o) {
  if (!Reflect.has(e, "as_item") || !Reflect.has(e, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const n = ye(), r = _e();
  de().set(void 0);
  const i = xe({
    slot: void 0,
    index: e._internal.index,
    subIndex: e._internal.subIndex
  }), l = be();
  typeof l == "number" && N(void 0);
  const u = ue();
  typeof e._internal.subIndex == "number" && N(e._internal.subIndex), n && n.subscribe((a) => {
    i.slotKey.set(a);
  }), Pe();
  const p = e.as_item, f = (a, _) => a ? {
    ...ee({
      ...a
    }, t),
    __render_slotParamsMappingFn: r ? G(r) : void 0,
    __render_as_item: _,
    __render_restPropsMapping: t
  } : void 0, m = b({
    ...e,
    _internal: {
      ...e._internal,
      index: l ?? e._internal.index
    },
    restProps: f(e.restProps, p),
    originalRestProps: e.restProps
  });
  return r && r.subscribe((a) => {
    m.update((_) => ({
      ..._,
      restProps: {
        ..._.restProps,
        __slotParamsMappingFn: a
      }
    }));
  }), [m, (a) => {
    var _;
    u((_ = a.restProps) == null ? void 0 : _.loading_status), m.set({
      ...a,
      _internal: {
        ...a._internal,
        index: l ?? a._internal.index
      },
      restProps: f(a.restProps, a.as_item),
      originalRestProps: a.restProps
    });
  }];
}
const Z = "$$ms-gr-slot-key";
function Pe() {
  S(Z, b(void 0));
}
function ye() {
  return I(Z);
}
const H = "$$ms-gr-component-slot-context-key";
function xe({
  slot: e,
  index: t,
  subIndex: o
}) {
  return S(H, {
    slotKey: b(e),
    slotIndex: b(t),
    subSlotIndex: b(o)
  });
}
function $e() {
  return I(H);
}
function T() {
  return T = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var o = arguments[t];
      for (var n in o) ({}).hasOwnProperty.call(o, n) && (e[n] = o[n]);
    }
    return e;
  }, T.apply(null, arguments);
}
var et = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function ve(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var J = {
  exports: {}
};
/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/
(function(e) {
  (function() {
    var t = {}.hasOwnProperty;
    function o() {
      for (var s = "", i = 0; i < arguments.length; i++) {
        var l = arguments[i];
        l && (s = r(s, n(l)));
      }
      return s;
    }
    function n(s) {
      if (typeof s == "string" || typeof s == "number")
        return s;
      if (typeof s != "object")
        return "";
      if (Array.isArray(s))
        return o.apply(null, s);
      if (s.toString !== Object.prototype.toString && !s.toString.toString().includes("[native code]"))
        return s.toString();
      var i = "";
      for (var l in s)
        t.call(s, l) && s[l] && (i = r(i, l));
      return i;
    }
    function r(s, i) {
      return i ? s ? s + " " + i : s + i : s;
    }
    e.exports ? (o.default = o, e.exports = o) : window.classNames = o;
  })();
})(J);
var Ce = J.exports;
const A = /* @__PURE__ */ ve(Ce), ke = /* @__PURE__ */ v.createContext({});
function Se() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: o,
    iconPrefixCls: n,
    theme: r
  } = v.useContext(B.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: o,
    iconPrefixCls: n
  };
}
const Me = (e) => {
  const {
    attachments: t,
    bubble: o,
    conversations: n,
    prompts: r,
    sender: s,
    suggestion: i,
    thoughtChain: l,
    welcome: u,
    theme: p,
    ...f
  } = e, {
    theme: m
  } = Se(), a = v.useMemo(() => ({
    attachments: t,
    bubble: o,
    conversations: n,
    prompts: r,
    sender: s,
    suggestion: i,
    thoughtChain: l,
    welcome: u
  }), [t, o, n, r, s, i, l, u]), _ = v.useMemo(() => ({
    ...m,
    ...p
  }), [m, p]);
  return /* @__PURE__ */ v.createElement(ke.Provider, {
    value: a
  }, /* @__PURE__ */ v.createElement(B, T({}, f, {
    // Note:  we can not set `cssVar` by default.
    //        Since when developer not wrap with XProvider,
    //        the generate css is still using css var but no css var injected.
    // Origin comment: antdx enable cssVar by default, and antd v6 will enable cssVar by default
    // theme={{ cssVar: true, ...antdConfProps?.theme }}
    theme: _
  })));
}, {
  SvelteComponent: Ke,
  assign: X,
  check_outros: Fe,
  claim_component: we,
  component_subscribe: O,
  compute_rest_props: z,
  create_component: je,
  create_slot: Ie,
  destroy_component: Oe,
  detach: Q,
  empty: j,
  exclude_internal_props: Te,
  flush: P,
  get_all_dirty_from_scope: Xe,
  get_slot_changes: Ee,
  get_spread_object: q,
  get_spread_update: Re,
  group_outros: Ne,
  handle_promise: Ae,
  init: ze,
  insert_hydration: U,
  mount_component: qe,
  noop: d,
  safe_not_equal: Le,
  transition_in: k,
  transition_out: M,
  update_await_block_branch: Be,
  update_slot_base: De
} = window.__gradio__svelte__internal;
function L(e) {
  let t, o, n = {
    ctx: e,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Ze,
    then: Ve,
    catch: Ge,
    value: 20,
    blocks: [, , ,]
  };
  return Ae(
    /*AwaitedXProvider*/
    e[2],
    n
  ), {
    c() {
      t = j(), n.block.c();
    },
    l(r) {
      t = j(), n.block.l(r);
    },
    m(r, s) {
      U(r, t, s), n.block.m(r, n.anchor = s), n.mount = () => t.parentNode, n.anchor = t, o = !0;
    },
    p(r, s) {
      e = r, Be(n, e, s);
    },
    i(r) {
      o || (k(n.block), o = !0);
    },
    o(r) {
      for (let s = 0; s < 3; s += 1) {
        const i = n.blocks[s];
        M(i);
      }
      o = !1;
    },
    d(r) {
      r && Q(t), n.block.d(r), n.token = null, n = null;
    }
  };
}
function Ge(e) {
  return {
    c: d,
    l: d,
    m: d,
    p: d,
    i: d,
    o: d,
    d
  };
}
function Ve(e) {
  let t, o;
  const n = [
    {
      className: A(
        "ms-gr-antdx-x-provider",
        /*$mergedProps*/
        e[0].elem_classes
      )
    },
    {
      id: (
        /*$mergedProps*/
        e[0].elem_id
      )
    },
    {
      style: (
        /*$mergedProps*/
        e[0].elem_style
      )
    },
    /*$mergedProps*/
    e[0].restProps,
    /*$mergedProps*/
    e[0].props,
    {
      slots: (
        /*$slots*/
        e[1]
      )
    },
    {
      component: Me
    },
    {
      themeMode: (
        /*$mergedProps*/
        e[0].gradio.theme
      )
    },
    {
      setSlotParams: (
        /*setSlotParams*/
        e[5]
      )
    }
  ];
  let r = {
    $$slots: {
      default: [Ye]
    },
    $$scope: {
      ctx: e
    }
  };
  for (let s = 0; s < n.length; s += 1)
    r = X(r, n[s]);
  return t = new /*XProvider*/
  e[20]({
    props: r
  }), {
    c() {
      je(t.$$.fragment);
    },
    l(s) {
      we(t.$$.fragment, s);
    },
    m(s, i) {
      qe(t, s, i), o = !0;
    },
    p(s, i) {
      const l = i & /*$mergedProps, $slots, setSlotParams*/
      35 ? Re(n, [i & /*$mergedProps*/
      1 && {
        className: A(
          "ms-gr-antdx-x-provider",
          /*$mergedProps*/
          s[0].elem_classes
        )
      }, i & /*$mergedProps*/
      1 && {
        id: (
          /*$mergedProps*/
          s[0].elem_id
        )
      }, i & /*$mergedProps*/
      1 && {
        style: (
          /*$mergedProps*/
          s[0].elem_style
        )
      }, i & /*$mergedProps*/
      1 && q(
        /*$mergedProps*/
        s[0].restProps
      ), i & /*$mergedProps*/
      1 && q(
        /*$mergedProps*/
        s[0].props
      ), i & /*$slots*/
      2 && {
        slots: (
          /*$slots*/
          s[1]
        )
      }, n[6], i & /*$mergedProps*/
      1 && {
        themeMode: (
          /*$mergedProps*/
          s[0].gradio.theme
        )
      }, i & /*setSlotParams*/
      32 && {
        setSlotParams: (
          /*setSlotParams*/
          s[5]
        )
      }]) : {};
      i & /*$$scope*/
      131072 && (l.$$scope = {
        dirty: i,
        ctx: s
      }), t.$set(l);
    },
    i(s) {
      o || (k(t.$$.fragment, s), o = !0);
    },
    o(s) {
      M(t.$$.fragment, s), o = !1;
    },
    d(s) {
      Oe(t, s);
    }
  };
}
function Ye(e) {
  let t;
  const o = (
    /*#slots*/
    e[16].default
  ), n = Ie(
    o,
    e,
    /*$$scope*/
    e[17],
    null
  );
  return {
    c() {
      n && n.c();
    },
    l(r) {
      n && n.l(r);
    },
    m(r, s) {
      n && n.m(r, s), t = !0;
    },
    p(r, s) {
      n && n.p && (!t || s & /*$$scope*/
      131072) && De(
        n,
        o,
        r,
        /*$$scope*/
        r[17],
        t ? Ee(
          o,
          /*$$scope*/
          r[17],
          s,
          null
        ) : Xe(
          /*$$scope*/
          r[17]
        ),
        null
      );
    },
    i(r) {
      t || (k(n, r), t = !0);
    },
    o(r) {
      M(n, r), t = !1;
    },
    d(r) {
      n && n.d(r);
    }
  };
}
function Ze(e) {
  return {
    c: d,
    l: d,
    m: d,
    p: d,
    i: d,
    o: d,
    d
  };
}
function He(e) {
  let t, o, n = (
    /*$mergedProps*/
    e[0].visible && L(e)
  );
  return {
    c() {
      n && n.c(), t = j();
    },
    l(r) {
      n && n.l(r), t = j();
    },
    m(r, s) {
      n && n.m(r, s), U(r, t, s), o = !0;
    },
    p(r, [s]) {
      /*$mergedProps*/
      r[0].visible ? n ? (n.p(r, s), s & /*$mergedProps*/
      1 && k(n, 1)) : (n = L(r), n.c(), k(n, 1), n.m(t.parentNode, t)) : n && (Ne(), M(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(r) {
      o || (k(n), o = !0);
    },
    o(r) {
      M(n), o = !1;
    },
    d(r) {
      r && Q(t), n && n.d(r);
    }
  };
}
function Je(e, t, o) {
  const n = ["gradio", "props", "as_item", "visible", "elem_id", "elem_classes", "elem_style", "_internal"];
  let r = z(t, n), s, i, l, {
    $$slots: u = {},
    $$scope: p
  } = t;
  const f = te(() => import("./config-provider-CivlQzIf.js").then((c) => c.f));
  let {
    gradio: m
  } = t, {
    props: a = {}
  } = t;
  const _ = b(a);
  O(e, _, (c) => o(15, s = c));
  let {
    as_item: g
  } = t, {
    visible: h = !0
  } = t, {
    elem_id: y = ""
  } = t, {
    elem_classes: K = []
  } = t, {
    elem_style: F = {}
  } = t, {
    _internal: w = {}
  } = t;
  const [E, W] = he({
    gradio: m,
    props: s,
    visible: h,
    _internal: w,
    elem_id: y,
    elem_classes: K,
    elem_style: F,
    as_item: g,
    restProps: r
  });
  O(e, E, (c) => o(0, i = c));
  const $ = ge(), R = me();
  return O(e, R, (c) => o(1, l = c)), ce("antd"), e.$$set = (c) => {
    t = X(X({}, t), Te(c)), o(19, r = z(t, n)), "gradio" in c && o(7, m = c.gradio), "props" in c && o(8, a = c.props), "as_item" in c && o(9, g = c.as_item), "visible" in c && o(10, h = c.visible), "elem_id" in c && o(11, y = c.elem_id), "elem_classes" in c && o(12, K = c.elem_classes), "elem_style" in c && o(13, F = c.elem_style), "_internal" in c && o(14, w = c._internal), "$$scope" in c && o(17, p = c.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty & /*props*/
    256 && _.update((c) => ({
      ...c,
      ...a
    })), W({
      gradio: m,
      props: s,
      visible: h,
      _internal: w,
      elem_id: y,
      elem_classes: K,
      elem_style: F,
      as_item: g,
      restProps: r
    });
  }, [i, l, f, _, E, $, R, m, a, g, h, y, K, F, w, s, u, p];
}
class Qe extends Ke {
  constructor(t) {
    super(), ze(this, t, Je, He, Le, {
      gradio: 7,
      props: 8,
      as_item: 9,
      visible: 10,
      elem_id: 11,
      elem_classes: 12,
      elem_style: 13,
      _internal: 14
    });
  }
  get gradio() {
    return this.$$.ctx[7];
  }
  set gradio(t) {
    this.$$set({
      gradio: t
    }), P();
  }
  get props() {
    return this.$$.ctx[8];
  }
  set props(t) {
    this.$$set({
      props: t
    }), P();
  }
  get as_item() {
    return this.$$.ctx[9];
  }
  set as_item(t) {
    this.$$set({
      as_item: t
    }), P();
  }
  get visible() {
    return this.$$.ctx[10];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), P();
  }
  get elem_id() {
    return this.$$.ctx[11];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), P();
  }
  get elem_classes() {
    return this.$$.ctx[12];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), P();
  }
  get elem_style() {
    return this.$$.ctx[13];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), P();
  }
  get _internal() {
    return this.$$.ctx[14];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), P();
  }
}
const tt = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: Qe
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  tt as X,
  b as Z,
  ve as a,
  et as c,
  $e as g,
  We as t
};
