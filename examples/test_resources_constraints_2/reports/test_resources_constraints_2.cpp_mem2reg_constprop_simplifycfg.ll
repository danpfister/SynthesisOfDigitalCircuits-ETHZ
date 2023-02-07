; ModuleID = 'test_resources_constraints_2.cpp_mem2reg_constprop.ll'
source_filename = "src/test_resources_constraints_2.cpp"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define i32 @_Z28test_resources_constraints_2iiii(i32 %a, i32 %b, i32 %c, i32 %n) #0 {
entry:
  %div = sdiv i32 %a, 2
  %mul = mul nsw i32 %b, 3
  %add = add nsw i32 %div, %mul
  %mul1 = mul nsw i32 %c, 5
  %add2 = add nsw i32 %add, %mul1
  %mul3 = mul nsw i32 %n, 7
  %add4 = add nsw i32 %add2, %mul3
  %add5 = add nsw i32 %n, %add4
  %mul6 = mul nsw i32 %a, 11
  %div7 = sdiv i32 %b, 13
  %add8 = add nsw i32 %mul6, %div7
  %mul9 = mul nsw i32 %c, 17
  %add10 = add nsw i32 %add8, %mul9
  %mul11 = mul nsw i32 %add5, 19
  %add12 = add nsw i32 %add10, %mul11
  %add13 = add nsw i32 %b, %add12
  %mul14 = mul nsw i32 %a, 23
  %mul15 = mul nsw i32 %add13, 29
  %add16 = add nsw i32 %mul14, %mul15
  %div17 = sdiv i32 %c, 31
  %add18 = add nsw i32 %add16, %div17
  %mul19 = mul nsw i32 %add5, 37
  %add20 = add nsw i32 %add18, %mul19
  %add21 = add nsw i32 %c, %add20
  %mul22 = mul nsw i32 %a, 41
  %mul23 = mul nsw i32 %add13, 43
  %add24 = add nsw i32 %mul22, %mul23
  %mul25 = mul nsw i32 %add21, 47
  %add26 = add nsw i32 %add24, %mul25
  %div27 = sdiv i32 %add5, 53
  %add28 = add nsw i32 %add26, %div27
  %add29 = add nsw i32 %a, %add28
  ret i32 %add29
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
  %call7 = call i32 @_Z28test_resources_constraints_2iiii(i32 %rem, i32 %rem2, i32 %rem4, i32 %rem6)
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
