; ModuleID = 'test_control_dependency_2.cpp.ll'
source_filename = "src/test_control_dependency_2.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define i32 @_Z25test_control_dependency_2iiii(i32 %a, i32 %b, i32 %c, i32 %n) #0 {
entry:
  %div = sdiv i32 %a, %c
  %shl = shl i32 %div, %b
  %sub = sub nsw i32 %n, 6
  %cmp = icmp sge i32 %shl, %sub
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %shr = ashr i32 %a, %n
  %mul = mul nsw i32 %shr, %b
  %div1 = sdiv i32 %mul, %b
  %shr2 = ashr i32 %div1, %c
  br label %if.end11

if.else:                                          ; preds = %entry
  %add = add nsw i32 %a, %b
  %shr3 = ashr i32 %n, %c
  %mul4 = mul nsw i32 %add, %shr3
  %cmp5 = icmp sle i32 %mul4, 42
  br i1 %cmp5, label %if.then6, label %if.else7

if.then6:                                         ; preds = %if.else
  br label %return

if.else7:                                         ; preds = %if.else
  %add8 = add nsw i32 %b, %a
  %mul9 = mul nsw i32 %add8, %n
  %shr10 = ashr i32 %mul9, %c
  br label %if.end

if.end:                                           ; preds = %if.else7
  br label %if.end11

if.end11:                                         ; preds = %if.end, %if.then
  %c.addr.0 = phi i32 [ %shr2, %if.then ], [ %c, %if.end ]
  %a.addr.0 = phi i32 [ %mul, %if.then ], [ %shr10, %if.end ]
  %add12 = add nsw i32 %a.addr.0, %b
  %shr13 = ashr i32 %n, %c.addr.0
  %mul14 = mul nsw i32 %add12, %shr13
  br label %return

return:                                           ; preds = %if.end11, %if.then6
  %retval.0 = phi i32 [ %mul14, %if.end11 ], [ %b, %if.then6 ]
  ret i32 %retval.0
}

; Function Attrs: noinline norecurse nounwind uwtable
define i32 @main() #1 {
entry:
  %call = call i32 @rand() #3
  %rem = srem i32 %call, 10
  %call1 = call i32 @rand() #3
  %rem2 = srem i32 %call1, 10
  %call3 = call i32 @rand() #3
  %rem4 = srem i32 %call3, 10
  %call5 = call i32 @rand() #3
  %rem6 = srem i32 %call5, 10
  %call7 = call i32 @_Z25test_control_dependency_2iiii(i32 %rem, i32 %rem2, i32 %rem4, i32 %rem6)
  ret i32 0
}

; Function Attrs: nounwind
declare i32 @rand() #2

attributes #0 = { noinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noinline norecurse nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { nounwind "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 6.0.1 (http://github.com/llvm-mirror/clang 2f27999df400d17b33cdd412fdd606a88208dfcc) (http://github.com/llvm-mirror/llvm 5136df4d089a086b70d452160ad5451861269498)"}
